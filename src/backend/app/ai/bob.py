import re
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from datetime import datetime

from app.config import settings
from app.ai.tools import ControlTowerTools

class BobAssistant:
    @staticmethod
    def process_query(query: str, db: Session) -> Dict[str, Any]:
        """
        Interprets user intent, invokes backend tools to retrieve live facts,
        and generates structured operational guidance.
        """
        q = query.lower()
        tools_called = []

        # Check for specific shipment mentioned e.g. "S-104", "SHP-104", "S-221"
        shipment_match = re.search(r'\b(s(?:hp)?[-_]?(\d+))\b', q)
        target_shipment_id = None
        if shipment_match:
            num = shipment_match.group(2)
            target_shipment_id = f"SHP-{num}"

        # 1. SPECIFIC SHIPMENT QUERY (e.g. "What should I do about shipment S-104?")
        if target_shipment_id:
            s_data = ControlTowerTools.get_shipment_risk(db, target_shipment_id)
            tools_called.append({"tool_name": "get_shipment_risk", "arguments": {"shipment_id": target_shipment_id}, "result": s_data})

            if "error" in s_data:
                return {
                    "answer": f"I couldn't locate {target_shipment_id} in the active shipment database.",
                    "direct_answer": f"Shipment {target_shipment_id} not found.",
                    "key_numbers": {"shipment_id": target_shipment_id},
                    "reasoning": "The queried shipment identifier does not match any current or delivered records.",
                    "recommended_actions": ["Verify shipment ID format (e.g. SHP-104, SHP-221)"],
                    "tools_called": tools_called
                }

            # Fetch route alternatives
            route_alts = ControlTowerTools.get_route_alternatives(db, target_shipment_id)
            tools_called.append({"tool_name": "get_route_alternatives", "arguments": {"shipment_id": target_shipment_id}, "result": route_alts})

            recommended_opt = next((r for r in route_alts if r.get("is_recommended")), route_alts[0] if route_alts else None)
            rec_name = recommended_opt.get("route_name", "Alternate Route") if recommended_opt else "Alternate Route"
            rec_exp = recommended_opt.get("explanation", s_data.get("recommended_action", "")) if recommended_opt else s_data.get("recommended_action", "")

            # Check if cold chain
            cold_info = ""
            if s_data.get("is_cold_chain"):
                temp_hist = ControlTowerTools.get_temperature_history(db, target_shipment_id)
                tools_called.append({"tool_name": "get_temperature_history", "arguments": {"shipment_id": target_shipment_id}, "result": temp_hist.get("analysis")})
                analysis = temp_hist.get("analysis", {})
                if analysis.get("has_excursion"):
                    cold_info = f" Note: Active temperature excursion detected ({analysis.get('current_temperature')}°C vs max {analysis.get('max_allowed')}°C)."

            direct_ans = f"Shipment {target_shipment_id} ({s_data['cargo_type']}, valued at ${s_data['cargo_value']:,.0f}) has {s_data['risk_level']} risk due to {s_data['disruption_exposure']}. Recommended action: {rec_name}.{cold_info}"
            
            return {
                "answer": f"{direct_ans}\n\nReasoning: {s_data['explanation']}\n\nOptimization Choice: {rec_exp}",
                "direct_answer": direct_ans,
                "key_numbers": {
                    "shipment_id": target_shipment_id,
                    "cargo_value": s_data["cargo_value"],
                    "risk_score": s_data["risk_score"],
                    "risk_level": s_data["risk_level"],
                    "delay_hours": s_data["delay_hours"]
                },
                "reasoning": f"{s_data['explanation']} Selected option: {rec_exp}",
                "recommended_actions": [
                    f"Authorize {rec_name}",
                    f"Notify carrier {s_data['carrier']} of priority dispatch",
                    f"Update consignee ETA to {recommended_opt.get('estimated_eta', 'revised window') if recommended_opt else 'revised schedule'}"
                ],
                "tools_called": tools_called
            }

        # 2. PORT STRIKE / WHAT HAPPENED / WHAT SHOULD I DO / OVERVIEW
        if any(term in q for term in ["strike", "port", "disruption", "what's happening", "what happened", "what should i do", "what should we do", "overview", "status", "summary"]):
            summary = ControlTowerTools.get_control_tower_summary(db)
            tools_called.append({"tool_name": "get_control_tower_summary", "arguments": {}, "result": summary})

            disruptions = ControlTowerTools.get_active_disruptions(db)
            tools_called.append({"tool_name": "get_active_disruptions", "arguments": {}, "result": disruptions})

            affected = ControlTowerTools.get_affected_shipments(db)
            tools_called.append({"tool_name": "get_affected_shipments", "arguments": {}, "result": f"{len(affected)} shipments"})

            redeployments = ControlTowerTools.get_redeployment_recommendations(db)
            tools_called.append({"tool_name": "get_redeployment_recommendations", "arguments": {}, "result": f"{len(redeployments)} recommendations"})

            cold_alerts = ControlTowerTools.get_cold_chain_alerts(db)
            tools_called.append({"tool_name": "get_cold_chain_alerts", "arguments": {}, "result": f"{len(cold_alerts)} alerts"})

            num_affected = len(affected) if affected else summary["at_risk_shipments"]
            critical_count = summary["critical_shipments"]
            val_at_risk = summary["cargo_value_at_risk"]
            redeploy_count = len(redeployments)

            # Check if any cold-chain alerts
            cold_notice = ""
            if cold_alerts:
                top_alert = cold_alerts[0]
                cold_notice = f" Shipment {top_alert['shipment_id']} also has an active cold-chain excursion ({top_alert.get('current_temperature')}°C) requiring immediate refrigeration intervention."

            disrupt_names = ", ".join([d["name"] for d in disruptions]) if disruptions else "No major disruptions active"

            val_formatted = f"${val_at_risk / 1_000_000:.1f}M" if val_at_risk >= 1_000_000 else f"${val_at_risk:,.0f}"

            direct_ans = (
                f"{num_affected} shipments are affected by active disruptions ({disrupt_names}). "
                f"{critical_count} are critical and approximately {val_formatted} of cargo is exposed. "
                f"I recommend rerouting high-risk shipments via multimodal corridors and redeploying {redeploy_count} idle fleet assets.{cold_notice}"
            )

            actions = [
                "Activate Alternate Route B (Multimodal Rail Bypass) for affected JNPT shipments",
                f"Deploy idle assets ({redeploy_count} available) to Ahmedabad-Mumbai and Mundra corridors",
                "Execute secondary container staging at Mundra Port to absorb diverted maritime volume"
            ]
            if cold_alerts:
                actions.insert(0, f"Dispatch urgent refrigeration intervention team for shipment {cold_alerts[0]['shipment_id']}")

            return {
                "answer": direct_ans,
                "direct_answer": direct_ans,
                "key_numbers": {
                    "affected_shipments": num_affected,
                    "critical_shipments": critical_count,
                    "cargo_value_at_risk": val_at_risk,
                    "idle_assets": summary["idle_fleet_assets"],
                    "redeployments_suggested": redeploy_count,
                    "cold_chain_alerts": len(cold_alerts)
                },
                "reasoning": (
                    f"Active disruptions include {disrupt_names}. Port congestion and sea weather delay schedules by 24-48 hours. "
                    f"Priority must be assigned to critical vaccines and electronics where time sensitivity and holding costs are highest."
                ),
                "recommended_actions": actions,
                "tools_called": tools_called
            }

        # 3. FLEET / IDLE / REDEPLOYMENT
        if any(term in q for term in ["fleet", "idle", "truck", "trucks", "asset", "assets", "redeploy", "utilization"]):
            idle_fleet = ControlTowerTools.get_idle_fleet(db)
            tools_called.append({"tool_name": "get_idle_fleet", "arguments": {}, "result": idle_fleet})

            redeployments = ControlTowerTools.get_redeployment_recommendations(db)
            tools_called.append({"tool_name": "get_redeployment_recommendations", "arguments": {}, "result": redeployments})

            idle_count = len(idle_fleet)
            redeploy_count = len(redeployments)

            top_redeploy = redeployments[0] if redeployments else None
            top_info = f" Specifically, {top_redeploy['recommendation']} ({top_redeploy['location']}) to {top_redeploy['affected_corridor']}." if top_redeploy else ""

            direct_ans = f"We currently have {idle_count} idle fleet assets available across key regional hubs. {redeploy_count} redeployment recommendations have been generated to alleviate congested corridors.{top_info}"

            return {
                "answer": direct_ans,
                "direct_answer": direct_ans,
                "key_numbers": {
                    "idle_assets_count": idle_count,
                    "redeployment_matches": redeploy_count
                },
                "reasoning": f"Assets with low utilization (<35%) at nearby hubs (Ahmedabad, Vadodara, Mundra) can be repositioned within 4 to 8 hours to absorb rerouted road freight.",
                "recommended_actions": [r["recommendation"] + f" for {r['affected_corridor']}" for r in redeployments[:3]] if redeployments else ["Maintain standing idle reserves"],
                "tools_called": tools_called
            }

        # 4. COLD CHAIN / TEMPERATURE / SENSOR / VACCINES
        if any(term in q for term in ["cold", "chain", "temp", "temperature", "excursion", "vaccine", "pharma", "sensor"]):
            alerts = ControlTowerTools.get_cold_chain_alerts(db)
            tools_called.append({"tool_name": "get_cold_chain_alerts", "arguments": {}, "result": alerts})

            if alerts:
                top = alerts[0]
                temp_hist = ControlTowerTools.get_temperature_history(db, top["shipment_id"])
                tools_called.append({"tool_name": "get_temperature_history", "arguments": {"shipment_id": top["shipment_id"]}, "result": temp_hist.get("analysis")})

                direct_ans = (
                    f"Alert: Shipment {top['shipment_id']} ({top['cargo_type']}) has recorded a {top['severity']} temperature excursion! "
                    f"Current reading is {top['current_temperature']}°C against allowed range of {top['allowed_range']}. Duration: {top['excursion_duration']}."
                )
                return {
                    "answer": direct_ans,
                    "direct_answer": direct_ans,
                    "key_numbers": {
                        "shipment_id": top["shipment_id"],
                        "current_temperature": top["current_temperature"],
                        "allowed_range": top["allowed_range"],
                        "duration": top["excursion_duration"],
                        "severity": top["severity"]
                    },
                    "reasoning": f"Thermal excursion exceeds critical bounds. Biological integrity may be compromised without immediate active cooling.",
                    "recommended_actions": [
                        "Initiate immediate refrigeration intervention and secondary telemetry verification",
                        "Assess cargo at nearest certified depot according to handling protocol",
                        "Notify quality assurance and supply chain dispatch officer"
                    ],
                    "tools_called": tools_called
                }
            else:
                direct_ans = "All cold-chain telemetry is currently within specified temperature thresholds (2°C to 8°C for biologics; -20°C for frozen freight). No active excursions detected."
                return {
                    "answer": direct_ans,
                    "direct_answer": direct_ans,
                    "key_numbers": {
                        "active_cold_chain_excursions": 0,
                        "status": "Nominal"
                    },
                    "reasoning": "Sensors across all active refrigerated fleet units are reporting steady nominal readings.",
                    "recommended_actions": ["Maintain standard IoT telemetry polling interval"],
                    "tools_called": tools_called
                }

        # 5. REROUTING / CARRIERS
        if any(term in q for term in ["reroute", "route", "carrier", "switch", "alternative"]):
            affected = ControlTowerTools.get_affected_shipments(db)
            tools_called.append({"tool_name": "get_affected_shipments", "arguments": {}, "result": f"{len(affected)} shipments"})

            high_risk = [s for s in affected if s.get("risk_level") in ["Critical", "High"]]
            count_reroute = len(high_risk)

            direct_ans = f"There are {count_reroute} high-risk shipments that should be immediately rerouted to avoid active bottlenecks. Alternate Route B (Multimodal Rail Corridor) and Alternate Route A (Express Highway) are primary options."
            return {
                "answer": direct_ans,
                "direct_answer": direct_ans,
                "key_numbers": {
                    "recommended_reroutes_count": count_reroute,
                    "average_delay_reduction_hours": 24.0
                },
                "reasoning": "Multimodal rail bypass reduces delay from +36 hours to +12 hours while maintaining cost delta under +5%.",
                "recommended_actions": [
                    f"Reroute shipment {s['shipment_id']} ({s['cargo_type']}) to bypass corridor"
                    for s in high_risk[:3]
                ],
                "tools_called": tools_called
            }

        # DEFAULT FALLBACK: Comprehensive Control Tower Status
        summary = ControlTowerTools.get_control_tower_summary(db)
        tools_called.append({"tool_name": "get_control_tower_summary", "arguments": {}, "result": summary})

        val_at_risk = summary.get('cargo_value_at_risk', 0.0)
        val_formatted = f"${val_at_risk / 1_000_000:.1f}M" if val_at_risk >= 1_000_000 else f"${val_at_risk:,.0f}"
        direct_ans = (
            f"Control Tower Status: {summary['active_shipments']} active shipments, with {summary['at_risk_shipments']} at risk "
            f"and {val_formatted} cargo value exposed. "
            f"{summary['idle_fleet_assets']} fleet assets are idle and available for redeployment. "
            f"{summary['cold_chain_alerts']} active cold-chain alerts."
        )

        return {
            "answer": direct_ans,
            "direct_answer": direct_ans,
            "key_numbers": summary,
            "reasoning": "Live monitoring across all multimodal corridors, disruptions, and IoT sensors.",
            "recommended_actions": [
                "Review high-risk shipments on the Shipments page",
                "Simulate Port Strike or Cold-Chain Excursions using top demo triggers",
                "Approve idle fleet redeployments"
            ],
            "tools_called": tools_called
        }
