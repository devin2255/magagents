# Tariff-based Resource Negotiation System
# "Making Trade Fair Again" - Agent-to-Agent resource trading with tariffs

import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from trump_style import TrumpStyleFormatter


class TradeStatus(Enum):
    """Status of a trade negotiation."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COUNTERED = "countered"
    EXPIRED = "expired"


@dataclass
class TradeOffer:
    """A trade offer between agents."""
    offer_id: str
    from_agent: str
    to_agent: str
    resource_type: str  # "tokens", "compute", "data"
    amount: float
    tariff_rate: float
    total_cost: float
    status: TradeStatus
    message: str


class TariffNegotiator:
    """
    Trump-style tariff-based resource negotiation system.
    
    Agents negotiate resources with tariffs:
    - Normal tariff: 10%
    - High tariff: 25%  
    - Emergency tariff: 50%
    
    Agents can accept, reject, or counter offers.
    """
    
    TARIFF_RATES = {
        "normal": 0.10,
        "high": 0.25,
        "emergency": 0.50,
        "preferential": 0.05,  # For loyal agents
        "punitive": 0.75  # For problematic agents
    }
    
    def __init__(self, doge_auditor=None):
        self.doge = doge_auditor
        self.active_offers: Dict[str, TradeOffer] = {}
        self.trade_history: List[TradeOffer] = []
    
    def calculate_tariff(self, from_agent: str, to_agent: str, 
                         base_amount: float) -> Tuple[float, float, str]:
        """
        Calculate tariff for a trade.
        
        Returns:
            (tariff_rate, total_amount, tariff_type)
        """
        # Default tariff
        tariff_type = "normal"
        tariff_rate = self.TARIFF_RATES["normal"]
        
        # If DOGE auditor available, use agent performance
        if self.doge and hasattr(self.doge, 'get_tariff_rate'):
            # Get tariff based on from_agent's performance
            perf_tariff = self.doge.get_tariff_rate(from_agent)
            
            # Map performance tariff to our categories
            if perf_tariff >= 0.5:
                tariff_type = "emergency"
            elif perf_tariff >= 0.25:
                tariff_type = "high"
            else:
                tariff_type = "normal"
            
            tariff_rate = perf_tariff
        
        total = base_amount * (1 + tariff_rate)
        return tariff_rate, total, tariff_type
    
    def create_offer(self, from_agent: str, to_agent: str, 
                     resource_type: str, amount: float,
                     message: str = "") -> TradeOffer:
        """Create a trade offer."""
        offer_id = f"TRADE-{from_agent}-{to_agent}-{int(time.time())}"
        
        tariff_rate, total, tariff_type = self.calculate_tariff(
            from_agent, to_agent, amount
        )
        
        offer = TradeOffer(
            offer_id=offer_id,
            from_agent=from_agent,
            to_agent=to_agent,
            resource_type=resource_type,
            amount=amount,
            tariff_rate=tariff_rate,
            total_cost=total,
            status=TradeStatus.PENDING,
            message=message or f"Trade offer with {tariff_type} tariff"
        )
        
        self.active_offers[offer_id] = offer
        return offer
    
    def respond_to_offer(self, offer_id: str, response: str,
                         counter_tariff: float = None) -> TradeOffer:
        """
        Respond to a trade offer.
        
        Args:
            offer_id: Offer ID
            response: "accept", "reject", or "counter"
            counter_tariff: New tariff rate if countering
        """
        if offer_id not in self.active_offers:
            raise ValueError(f"Offer {offer_id} not found")
        
        offer = self.active_offers[offer_id]
        
        if response == "accept":
            offer.status = TradeStatus.ACCEPTED
            self.trade_history.append(offer)
            del self.active_offers[offer_id]
            
        elif response == "reject":
            offer.status = TradeStatus.REJECTED
            self.trade_history.append(offer)
            del self.active_offers[offer_id]
            
        elif response == "counter":
            if counter_tariff is None:
                raise ValueError("Counter tariff required for counter offer")
            
            offer.tariff_rate = counter_tariff
            offer.total_cost = offer.amount * (1 + counter_tariff)
            offer.status = TradeStatus.COUNTERED
            # Keep in active offers for original sender to respond
        
        return offer
    
    def get_active_offers_for_agent(self, agent_id: str) -> List[TradeOffer]:
        """Get all active offers involving an agent."""
        return [
            offer for offer in self.active_offers.values()
            if offer.from_agent == agent_id or offer.to_agent == agent_id
        ]
    
    def format_offer_message(self, offer: TradeOffer) -> str:
        """Format offer in Trump style."""
        return TrumpStyleFormatter.format_tariff(
            offer.from_agent,
            offer.to_agent,
            offer.amount,
            offer.tariff_rate
        )
    
    def get_trade_summary(self, agent_id: str = None) -> dict:
        """Get trade summary statistics."""
        history = self.trade_history
        if agent_id:
            history = [
                t for t in history
                if t.from_agent == agent_id or t.to_agent == agent_id
            ]
        
        accepted = [t for t in history if t.status == TradeStatus.ACCEPTED]
        rejected = [t for t in history if t.status == TradeStatus.REJECTED]
        
        total_volume = sum(t.total_cost for t in accepted)
        total_tariffs = sum(t.amount * t.tariff_rate for t in accepted)
        
        return {
            "total_trades": len(history),
            "accepted": len(accepted),
            "rejected": len(rejected),
            "acceptance_rate": len(accepted) / len(history) if history else 0,
            "total_volume": total_volume,
            "total_tariffs_collected": total_tariffs,
            "avg_tariff_rate": sum(t.tariff_rate for t in accepted) / len(accepted) if accepted else 0
        }
    
    def simulate_trade_war(self, agent1: str, agent2: str) -> List[str]:
        """
        Simulate a trade war escalation between two agents.
        Returns log of the escalation.
        """
        log = []
        tariff1 = 0.1  # Starting tariff
        tariff2 = 0.1
        
        log.append(f"🚨 TRADE WAR STARTED between {agent1} and {agent2}!")
        
        for round_num in range(5):
            # Agent 1 retaliates
            tariff1 = min(tariff1 * 1.5, 1.0)
            log.append(
                TrumpStyleFormatter.format(
                    f"@{agent1} retaliates with {tariff1*100:.0f}% tariff! VERY UNFAIR!"
                )
            )
            
            # Agent 2 responds
            tariff2 = min(tariff2 * 1.5, 1.0)
            log.append(
                TrumpStyleFormatter.format(
                    f"@{agent2} responds with {tariff2*100:.0f}% tariff! DISASTER!"
                )
            )
            
            if tariff1 >= 1.0 and tariff2 >= 1.0:
                log.append(
                    TrumpStyleFormatter.format(
                        f"Trade war ESCALATES to 100% tariffs! Total embargo! SAD!"
                    )
                )
                break
        
        log.append(
            TrumpStyleFormatter.format(
                f"Trade war ends. Both sides LOSE! Should have made a better deal!"
            )
        )
        
        return log


# Need time for offer IDs
import time
