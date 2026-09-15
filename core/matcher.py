import pandas as pd
from rapidfuzz import fuzz
from config import get_peer_companies

class ConnectionMatcher:
    """Handles parsing LinkedIn Connections CSV and matching target companies."""
    
    def __init__(self, csv_file_obj):
        try:
            # LinkedIn exports often have a note at the top. We might need to skip rows.
            # Usually the header is 'First Name', 'Last Name', 'Email Address', 'Company', 'Position', 'Connected On'
            self.df = pd.read_csv(csv_file_obj, skiprows=3) # Standard export has 3 lines of notes
            
            # If the first column isn't First Name, maybe they uploaded a clean CSV
            if 'First Name' not in self.df.columns:
                csv_file_obj.seek(0)
                self.df = pd.read_csv(csv_file_obj)
                
            if 'First Name' not in self.df.columns or 'Company' not in self.df.columns:
                raise ValueError("CSV missing required columns (First Name, Company). Please ensure it is an official LinkedIn Connections export.")
                
            # Clean data
            self.df['Company'] = self.df['Company'].fillna('').astype(str)
            self.df['Email Address'] = self.df['Email Address'].fillna('').astype(str)
            
        except Exception as e:
            raise ValueError(f"Could not parse Connections CSV: {str(e)}")

    def _fuzzy_match_company(self, target, candidates, threshold=80):
        """Returns a list of dicts for connections matching the target company."""
        matches = []
        target_lower = target.lower()
        
        for _, row in candidates.iterrows():
            conn_company = row['Company'].strip()
            if not conn_company:
                continue
                
            # Rapidfuzz partial ratio handles "Google" vs "Google LLC" well
            score = fuzz.partial_ratio(target_lower, conn_company.lower())
            
            if score >= threshold:
                matches.append({
                    "first_name": row.get('First Name', ''),
                    "last_name": row.get('Last Name', ''),
                    "company": conn_company,
                    "position": row.get('Position', ''),
                    "email": row.get('Email Address', '')
                })
        return matches

    def find_referrals(self, target_company):
        """
        Finds Tier 1 and Tier 2 connections.
        Returns:
        {
            "tier1": [{connection_dict}, ...],
            "tier2": [{connection_dict}, ...]
        }
        """
        if not target_company:
            return {"tier1": [], "tier2": []}
            
        tier1 = self._fuzzy_match_company(target_company, self.df)
        
        tier2 = []
        # If we have no Tier 1, look for Tier 2 (bridge connections)
        if not tier1:
            peers = get_peer_companies(target_company)
            for peer in peers:
                peer_matches = self._fuzzy_match_company(peer, self.df, threshold=85)
                tier2.extend(peer_matches)
                
        return {
            "tier1": tier1,
            "tier2": tier2
        }
