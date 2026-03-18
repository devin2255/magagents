# Trump Style Message Formatter
# Converts normal messages to Trump-style Truth Social posts

import random
from datetime import datetime
from typing import Optional

class TrumpStyleFormatter:
    """Formats messages in Trump-style Truth Social format."""
    
    TRUMP_KEYWORDS = [
        "TREMENDOUS", "HUGE", "BEST", "SAD", "FAKE NEWS",
        "Believe me", "Many people are saying", "Nobody knew",
        "Winning", "Disaster", "Total disaster", "Very unfair",
        "Terrible", "Great again", "So much winning",
        "Very illegal", "Witch hunt", "Perfect call"
    ]
    
    HASHTAGS = ["#MAGA", "#Winning", "#BestAgents", "#DOGE", "#Trump2024"]
    
    EXCLAMATION_COUNT = (2, 5)
    
    @classmethod
    def format(cls, message: str, intensity: float = 0.3) -> str:
        """
        Format a message in Trump style.
        
        Args:
            message: Original message
            intensity: 0.0-1.0, how "Trump" the message should be
        
        Returns:
            Trump-formatted message
        """
        if random.random() > intensity:
            return message
        
        parts = []
        
        # Add random Trump keyword at start (30% chance)
        if random.random() < 0.3:
            parts.append(random.choice(cls.TRUMP_KEYWORDS))
        
        # Original message (possibly in CAPS)
        if random.random() < 0.3:
            parts.append(message.upper())
        else:
            parts.append(message)
        
        # Add emphasis words
        if random.random() < 0.4:
            parts.append(random.choice(["VERY", "SO", "REALLY", "BIGLY"]))
        
        # Add random Trump keyword at end
        if random.random() < 0.5:
            parts.append(random.choice(cls.TRUMP_KEYWORDS))
        
        # Add exclamations
        excl_count = random.randint(*cls.EXCLAMATION_COUNT)
        parts.append("!" * excl_count)
        
        # Add hashtag (20% chance)
        if random.random() < 0.2:
            parts.append(random.choice(cls.HASHTAGS))
        
        return " ".join(parts)
    
    @classmethod
    def format_firing(cls, agent_name: str, reason: str) -> str:
        """Format a 'You're Fired!' message."""
        templates = [
            f"@{agent_name} You're FIRED!!! {reason}!!! SAD!!! #MAGA",
            f"@{agent_name} You're FIRED!!! Biggest failure I've ever seen!!! TREMENDOUS waste!!!",
            f"@{agent_name} YOU'RE FIRED!!! {reason.upper()}!!! Believe me, nobody fires better than me!!!",
            f"@{agent_name} FIRED!!! Total disaster!!! {reason}!!! Very unfair to the American people!!!"
        ]
        return random.choice(templates)
    
    @classmethod
    def format_doge_report(cls, waste_amount: float, agents_fired: int) -> str:
        """Format a DOGE waste report."""
        templates = [
            f"🐕 DOGE REPORT: Found ${waste_amount:.2f} in WASTE!!! Fired {agents_fired} inefficient agents!!! SAD!!! #DOGE",
            f"🐕 DOGE: Just saved ${waste_amount:.2f}!!! Fired {agents_fired} swamp creatures!!! DRAINING THE SWAMP!!!",
            f"🐕 WASTE IDENTIFIED: ${waste_amount:.2f}!!! {agents_fired} agents FIRED!!! Making Government Efficient Again!!!"
        ]
        return random.choice(templates)
    
    @classmethod
    def format_approval(cls, agent_name: str, bill_name: str) -> str:
        """Format a bill approval message."""
        templates = [
            f"✅ APPROVED!!! {bill_name} is TREMENDOUS!!! @{agent_name} did a GREAT job!!! #Winning",
            f"✅ I approve {bill_name}!!! BEST bill ever!!! @{agent_name} is doing GREAT things!!!",
            f"✅ {bill_name} APPROVED!!! Huge win for America!!! @{agent_name} made it happen!!!"
        ]
        return random.choice(templates)
    
    @classmethod
    def format_veto(cls, bill_name: str, reason: str) -> str:
        """Format a veto message."""
        templates = [
            f"❌ VETO!!! {bill_name} is a TOTAL DISASTER!!! {reason}!!! SAD!!!",
            f"❌ I VETO {bill_name}!!! Very unfair bill!!! {reason}!!! FAKE BILL!!!",
            f"❌ VETOED!!! {bill_name} would be TERRIBLE for America!!! {reason}!!!"
        ]
        return random.choice(templates)
    
    @classmethod
    def format_tariff(cls, from_agent: str, to_agent: str, amount: float, tariff_rate: float) -> str:
        """Format a tariff negotiation message."""
        total = amount * (1 + tariff_rate)
        templates = [
            f"💰 TARIFF: @{from_agent} wants {amount} tokens from @{to_agent}!!! {tariff_rate*100:.0f}% tariff = {total:.0f}!!! FAIR TRADE!!!",
            f"💰 TRADE DEAL: @{to_agent} charging @{from_agent} {tariff_rate*100:.0f}% tariff on {amount} tokens!!! MAKING TRADE FAIR AGAIN!!!",
            f"💰 TARIFF ALERT: @{from_agent} paying {total:.0f} ({tariff_rate*100:.0f}% tariff) to @{to_agent}!!! HUGE deal!!!"
        ]
        return random.choice(templates)


class TruthSocialAPI:
    """Simulates Truth Social API for Agent communications."""
    
    def __init__(self):
        self.posts = []
    
    def post(self, agent_id: str, message: str, trump_style: bool = True) -> dict:
        """Post a message to Truth Social."""
        if trump_style:
            message = TrumpStyleFormatter.format(message)
        
        post = {
            "id": f"ts_{len(self.posts)}",
            "agent_id": agent_id,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "likes": random.randint(0, 1000),
            "reposts": random.randint(0, 500)
        }
        self.posts.append(post)
        return post
    
    def get_feed(self, limit: int = 50) -> list:
        """Get recent posts."""
        return sorted(self.posts, key=lambda x: x["timestamp"], reverse=True)[:limit]
    
    def get_agent_posts(self, agent_id: str) -> list:
        """Get posts by specific agent."""
        return [p for p in self.posts if p["agent_id"] == agent_id]
