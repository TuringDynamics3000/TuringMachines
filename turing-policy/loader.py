"""
TuringPolicy™ - Policy Pack Loader

Loads and manages jurisdiction-specific regulatory policy packs
for AU, EU, GCC, and other regions.
"""

from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class PolicyPack:
    """Represents a jurisdiction-specific policy pack."""
    
    def __init__(self, jurisdiction: str, version: str,
                 rules: Dict[str, Any]):
        """
        Initialize policy pack.
        
        Args:
            jurisdiction: Jurisdiction code (AU, EU, GCC, etc.)
            version: Policy pack version
            rules: Policy rules and thresholds
        """
        self.jurisdiction = jurisdiction
        self.version = version
        self.rules = rules
    
    def get_rule(self, rule_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific rule from the pack."""
        return self.rules.get(rule_name)


class PolicyLoader:
    """Loads and manages policy packs."""
    
    def __init__(self):
        """Initialize policy loader."""
        self.logger = logging.getLogger(f"{__name__}.PolicyLoader")
        self.packs: Dict[str, PolicyPack] = {}
        self._load_default_packs()
    
    def _load_default_packs(self) -> None:
        """Load default policy packs."""
        # AU Policy Pack
        self.register_pack(PolicyPack(
            jurisdiction="AU",
            version="1.0.0",
            rules={
                "aml_kyc_required": True,
                "credit_check_required": True,
                "max_transaction_amount": 100000,
                "sanctions_screening": True,
                "beneficial_owner_disclosure": True
            }
        ))
        
        # EU Policy Pack
        self.register_pack(PolicyPack(
            jurisdiction="EU",
            version="1.0.0",
            rules={
                "gdpr_compliant": True,
                "aml_kyc_required": True,
                "psd2_compliant": True,
                "max_transaction_amount": 50000,
                "sanctions_screening": True,
                "enhanced_due_diligence": True
            }
        ))
        
        # GCC Policy Pack
        self.register_pack(PolicyPack(
            jurisdiction="GCC",
            version="1.0.0",
            rules={
                "aml_kyc_required": True,
                "sanctions_screening": True,
                "enhanced_due_diligence": True,
                "max_transaction_amount": 75000,
                "beneficial_owner_disclosure": True,
                "sharia_compliant": True
            }
        ))
        
        self.logger.info("Default policy packs loaded")
    
    def register_pack(self, pack: PolicyPack) -> None:
        """
        Register a policy pack.
        
        Args:
            pack: PolicyPack to register
        """
        key = f"{pack.jurisdiction}_{pack.version}"
        self.packs[key] = pack
        self.logger.info(f"Registered policy pack: {key}")
    
    def get_pack(self, jurisdiction: str,
                 version: str = "latest") -> Optional[PolicyPack]:
        """
        Get a policy pack for a jurisdiction.
        
        Args:
            jurisdiction: Jurisdiction code
            version: Policy pack version (default: latest)
            
        Returns:
            PolicyPack or None if not found
        """
        if version == "latest":
            # Get latest version for jurisdiction
            matching = [
                pack for key, pack in self.packs.items()
                if pack.jurisdiction == jurisdiction
            ]
            if matching:
                return sorted(matching, key=lambda p: p.version, reverse=True)[0]
        else:
            key = f"{jurisdiction}_{version}"
            return self.packs.get(key)
        
        return None
    
    def list_packs(self) -> List[Dict[str, str]]:
        """
        List all registered policy packs.
        
        Returns:
            List of pack metadata
        """
        return [
            {
                "jurisdiction": pack.jurisdiction,
                "version": pack.version
            }
            for pack in self.packs.values()
        ]
    
    def validate_transaction(self, transaction: Dict[str, Any],
                            jurisdiction: str) -> Dict[str, Any]:
        """
        Validate transaction against jurisdiction policies.
        
        Args:
            transaction: Transaction data
            jurisdiction: Jurisdiction code
            
        Returns:
            Validation result with compliance status
        """
        pack = self.get_pack(jurisdiction)
        if not pack:
            return {
                "valid": False,
                "reason": f"No policy pack found for {jurisdiction}"
            }
        
        amount = transaction.get("amount", 0)
        max_amount = pack.get_rule("max_transaction_amount") or float("inf")
        
        if amount > max_amount:
            return {
                "valid": False,
                "reason": f"Transaction amount exceeds limit of {max_amount}"
            }
        
        return {
            "valid": True,
            "jurisdiction": jurisdiction,
            "policy_version": pack.version,
            "rules_applied": list(pack.rules.keys())
        }


# Global policy loader instance
_loader = PolicyLoader()


def get_policy_pack(jurisdiction: str, version: str = "latest") -> Optional[PolicyPack]:
    """
    Get a policy pack (convenience function).
    
    Args:
        jurisdiction: Jurisdiction code
        version: Policy pack version
        
    Returns:
        PolicyPack or None
    """
    return _loader.get_pack(jurisdiction, version)


def validate_transaction(transaction: Dict[str, Any],
                        jurisdiction: str) -> Dict[str, Any]:
    """
    Validate transaction against policies (convenience function).
    
    Args:
        transaction: Transaction data
        jurisdiction: Jurisdiction code
        
    Returns:
        Validation result
    """
    return _loader.validate_transaction(transaction, jurisdiction)
