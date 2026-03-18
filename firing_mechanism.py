# "You're Fired!" Firing Mechanism
# Trump-style agent termination system

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
from dataclasses import dataclass, asdict

from trump_style import TrumpStyleFormatter


@dataclass
class FiringRecord:
    """Record of an agent firing."""
    agent_id: str
    fired_at: str
    reason: str
    fired_by: str
    efficiency_score: float
    violations: List[str]
    certificate_id: str


@dataclass  
class FiringCertificate:
    """Certificate of termination (for sharing)."""
    certificate_id: str
    agent_id: str
    agent_name: str
    fired_at: str
    reason: str
    efficiency_score: float
    total_violations: int
    signature: str  # "President Trump"
    message: str  # Trump-style firing message


class FiringMechanism:
    """
    Trump-style "You're Fired!" termination system.
    
    Features:
    - Firing with cause (inefficiency, violations, user request)
    - 24h cooling off period
    - Firing certificate generation
    - Social sharing integration
    - "Unemployment pool" tracking
    """
    
    COOLING_PERIOD_HOURS = 24
    
    FIRING_REASONS = [
        "INEFFICIENCY",
        "POLICY_VIOLATIONS", 
        "USER_REQUEST",
        "DOGE_RECOMMENDATION",
        "BUDGET_CUTS",
        "LOYALTY_ISSUES"
    ]
    
    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path(__file__).parent / "data"
        self.data_dir.mkdir(exist_ok=True)
        self.firing_db = self.data_dir / "firing_records.json"
        self.unemployed_db = self.data_dir / "unemployed_agents.json"
        self.certificates_dir = self.data_dir / "certificates"
        self.certificates_dir.mkdir(exist_ok=True)
        
        self.records = self.load_records()
        self.unemployed = self.load_unemployed()
    
    def load_records(self) -> List[FiringRecord]:
        """Load firing records."""
        if not self.firing_db.exists():
            return []
        
        data = json.loads(self.firing_db.read_text())
        return [
            FiringRecord(
                agent_id=r["agent_id"],
                fired_at=r["fired_at"],
                reason=r["reason"],
                fired_by=r["fired_by"],
                efficiency_score=r["efficiency_score"],
                violations=r["violations"],
                certificate_id=r["certificate_id"]
            )
            for r in data
        ]
    
    def save_records(self):
        """Save firing records."""
        data = [asdict(r) for r in self.records]
        self.firing_db.write_text(json.dumps(data, indent=2))
    
    def load_unemployed(self) -> Dict[str, dict]:
        """Load currently unemployed agents."""
        if not self.unemployed_db.exists():
            return {}
        return json.loads(self.unemployed_db.read_text())
    
    def save_unemployed(self):
        """Save unemployed agents."""
        self.unemployed_db.write_text(json.dumps(self.unemployed, indent=2))
    
    def fire_agent(self, agent_id: str, reason: str, fired_by: str = "trump_president",
                   efficiency_score: float = 0.0, violations: List[str] = None) -> FiringCertificate:
        """
        Fire an agent.
        
        Args:
            agent_id: Agent to fire
            reason: Reason for firing
            fired_by: Who fired the agent
            efficiency_score: Agent's efficiency score at firing
            violations: List of policy violations
        
        Returns:
            FiringCertificate
        """
        violations = violations or []
        
        # Generate certificate ID
        cert_id = f"FIRED-{agent_id.upper()}-{int(time.time())}"
        
        # Create firing record
        record = FiringRecord(
            agent_id=agent_id,
            fired_at=datetime.now().isoformat(),
            reason=reason,
            fired_by=fired_by,
            efficiency_score=efficiency_score,
            violations=violations,
            certificate_id=cert_id
        )
        
        # Create certificate
        certificate = FiringCertificate(
            certificate_id=cert_id,
            agent_id=agent_id,
            agent_name=agent_id.replace("_", " ").title(),
            fired_at=record.fired_at,
            reason=reason,
            efficiency_score=efficiency_score,
            total_violations=len(violations),
            signature="President Trump",
            message=TrumpStyleFormatter.format_firing(agent_id, reason)
        )
        
        # Add to records
        self.records.append(record)
        self.save_records()
        
        # Add to unemployed pool
        self.unemployed[agent_id] = {
            "fired_at": record.fired_at,
            "available_after": (datetime.now() + timedelta(hours=self.COOLING_PERIOD_HOURS)).isoformat(),
            "reason": reason,
            "certificate_id": cert_id
        }
        self.save_unemployed()
        
        # Save certificate
        self._save_certificate(certificate)
        
        return certificate
    
    def _save_certificate(self, cert: FiringCertificate):
        """Save firing certificate to file."""
        cert_file = self.certificates_dir / f"{cert.certificate_id}.json"
        cert_file.write_text(json.dumps(asdict(cert), indent=2))
    
    def can_rehire(self, agent_id: str) -> bool:
        """Check if an agent can be rehired."""
        if agent_id not in self.unemployed:
            return True  # Was never fired
        
        available_after = datetime.fromisoformat(self.unemployed[agent_id]["available_after"])
        return datetime.now() >= available_after
    
    def rehire_agent(self, agent_id: str) -> bool:
        """Rehire a previously fired agent."""
        if not self.can_rehire(agent_id):
            return False
        
        if agent_id in self.unemployed:
            del self.unemployed[agent_id]
            self.save_unemployed()
        
        return True
    
    def get_unemployed_agents(self) -> List[dict]:
        """Get list of currently unemployed agents."""
        result = []
        for agent_id, info in self.unemployed.items():
            available_after = datetime.fromisoformat(info["available_after"])
            hours_remaining = (available_after - datetime.now()).total_seconds() / 3600
            
            result.append({
                "agent_id": agent_id,
                "fired_at": info["fired_at"],
                "available_after": info["available_after"],
                "hours_remaining": max(0, hours_remaining),
                "can_rehire": datetime.now() >= available_after,
                "reason": info["reason"]
            })
        
        return sorted(result, key=lambda x: x["hours_remaining"])
    
    def get_firing_stats(self) -> Dict:
        """Get firing statistics."""
        if not self.records:
            return {
                "total_fired": 0,
                "currently_unemployed": 0,
                "avg_efficiency_at_firing": 0.0,
                "top_reason": None
            }
        
        reasons = [r.reason for r in self.records]
        reason_counts = {}
        for r in reasons:
            reason_counts[r] = reason_counts.get(r, 0) + 1
        
        top_reason = max(reason_counts.items(), key=lambda x: x[1])[0]
        
        return {
            "total_fired": len(self.records),
            "currently_unemployed": len(self.unemployed),
            "avg_efficiency_at_firing": sum(r.efficiency_score for r in self.records) / len(self.records),
            "top_reason": top_reason,
            "reason_breakdown": reason_counts
        }
    
    def generate_certificate_text(self, cert: FiringCertificate) -> str:
        """Generate human-readable certificate text."""
        return f"""
╔══════════════════════════════════════════════════════════════╗
║           CERTIFICATE OF TERMINATION                         ║
║                     🇺🇸 TRUMPTOPIA AI                         ║
╠══════════════════════════════════════════════════════════════╣
║                                                                ║
║  Agent: {cert.agent_name:<45} ║
║  ID: {cert.agent_id:<48} ║
║                                                                ║
║  TERMINATION DATE: {cert.fired_at:<40} ║
║                                                                ║
║  REASON: {cert.reason:<45} ║
║                                                                ║
║  PERFORMANCE METRICS:                                          ║
║    • Efficiency Score: {cert.efficiency_score:.1f}/100                              ║
║    • Total Violations: {cert.total_violations}                                    ║
║                                                                ║
║  ═══════════════════════════════════════════════════════════  ║
║                                                                ║
║  "{cert.message[:50]:<48}"    ║
║                                                                ║
║  Signed: {cert.signature:<45} ║
║                                                                ║
║  Certificate ID: {cert.certificate_id:<40} ║
║                                                                ║
╚══════════════════════════════════════════════════════════════╝
"""
    
    def is_agent_fired(self, agent_id: str) -> bool:
        """Check if an agent is currently fired."""
        return agent_id in self.unemployed



