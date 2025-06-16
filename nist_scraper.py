"""
NIST WebBook Scraper
Author: Avory Campbell
Columbia University, Department of Computer Science

Fetches thermodynamic data (enthalpy, entropy) from the NIST Chemistry WebBook by parsing HTML pages.
Used as a live data source to support accurate, real-time analysis of chemical species.
"""
import requests
from bs4 import BeautifulSoup

def fetch_nist_data(formula):
    """
    Fetch thermochemical data (ΔH, ΔS, ΔG) from NIST Chemistry WebBook for a given chemical formula.

    Args:
        formula (str): Chemical formula (e.g., 'H2O', 'CO2')

    Returns:
        dict: {'deltaH': value in kJ/mol, 'deltaS': value in J/mol·K, 'deltaG': value in kJ/mol}
              Returns None if data not found.
    """
    base_url = "https://webbook.nist.gov/cgi/cbook.cgi"
    params = {
        'Formula': formula,
        'NoIon': 1,
        'Units': 2,
        'Type': 'Thermo-Condensed'
    }

    try:
        # Step 1: Search for the compound
        search_resp = requests.get(base_url, params=params)
        search_resp.raise_for_status()
        search_soup = BeautifulSoup(search_resp.text, 'html.parser')

        # Step 2: Find the link to thermochemical data page
        # Usually it's the first link under 'Thermochemical Data' section
        thermo_link = None
        for a_tag in search_soup.find_all('a', href=True):
            href = a_tag['href']
            if 'thermo' in href.lower():
                thermo_link = href
                break

        if not thermo_link:
            print(f"No thermochemical data found for {formula}")
            return None

        # Construct full URL for thermo page
        thermo_url = f"https://webbook.nist.gov{thermo_link}"

        # Step 3: Request the thermochemical data page
        thermo_resp = requests.get(thermo_url)
        thermo_resp.raise_for_status()
        thermo_soup = BeautifulSoup(thermo_resp.text, 'html.parser')

        # Step 4: Parse ΔH, ΔS, and ΔG from the thermo table
        data = {'deltaH': None, 'deltaS': None, 'deltaG': None}

        # Look for table rows with relevant properties
        for tr in thermo_soup.find_all('tr'):
            tds = tr.find_all('td')
            if len(tds) < 2:
                continue
            prop_name = tds[0].get_text(strip=True)
            value_text = tds[1].get_text(strip=True)

            if 'Standard Enthalpy of Formation' in prop_name:
                # Extract numeric value and convert kcal/mol to kJ/mol if necessary
                try:
                    val = float(value_text.split()[0])
                    # NIST reports in kJ/mol, so no conversion needed
                    data['deltaH'] = val
                except:
                    pass
            elif 'Standard Entropy' in prop_name:
                try:
                    val = float(value_text.split()[0])
                    data['deltaS'] = val
                except:
                    pass
            elif 'Standard Gibbs Energy of Formation' in prop_name:
                try:
                    val = float(value_text.split()[0])
                    data['deltaG'] = val
                except:
                    pass

        if all(v is None for v in data.values()):
            print(f"Thermochemical data incomplete or missing for {formula}")
            return None

        return data

    except Exception as e:
        print(f"Error fetching data for {formula}: {e}")
        return None

