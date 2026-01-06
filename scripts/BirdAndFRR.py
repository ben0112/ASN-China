import requests
from lxml import etree

def fetch_asns():
    """
    Fetches ASN numbers from the specified URL and returns them as a list.
    """
    url = "https://bgp.he.net/country/CN"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
    }
    r = requests.get(url=url, headers=headers).text
    tree = etree.HTML(r)
    asns = tree.xpath('//*[@id="asns"]/tbody/tr')
    asn_list = []
    for asn in asns:
        asn_number = asn.xpath('td[1]/a')[0].text.replace('AS', '')
        asn_name = asn.xpath('td[2]')[0].text
        if asn_name is not None:
            asn_list.append(asn_number)
    return asn_list

def save_asns_to_file(asn_list, filename="china_asns.txt"):
    """
    Saves the list of ASN numbers to the specified file, one per line.
    """
    with open(filename, "w") as asn_file:
        for asn in asn_list:
            asn_file.write(asn + "\n")

def generate_bird_config(asn_list, config_filename="bird_filter.conf"):
    """
    Generates a Bird BGP filter configuration file using the provided ASN list.
    """
    asn_set_str = ', '.join(asn_list)
    define_statement = f"define china_asns = [{asn_set_str}];"
    filter_definition = """
filter block_china {
    if bgp_path.last ~ china_asns then reject;
    accept;
}
"""
    with open(config_filename, "w") as config_file:
        config_file.write(define_statement + '\n\n')
        config_file.write(filter_definition)

# ============================================================================
# NEW FUNCTION ADDED: Generate FRR configuration
# ============================================================================
def generate_frr_config(asn_list, config_filename="frr_filter.conf"):
    """
    Generates an FRR BGP filter configuration file using the provided ASN list.
    """
    with open(config_filename, "w") as config_file:
        # Write header comment
        config_file.write("! FRR BGP filter configuration to block Chinese ASNs\n")
        config_file.write("! Auto-generated from https://bgp.he.net/country/CN\n")
        config_file.write(f"! Total ASNs: {len(asn_list)}\n")
        config_file.write("!\n")
        
        # Generate AS-path access list entries
        config_file.write("! AS-path access list for blocking Chinese ASNs\n")
        config_file.write("! The $ at the end matches the last ASN in the path (origin AS)\n")
        for asn in asn_list:
            config_file.write(f"ip as-path access-list CHINA_ASN permit _{asn}$\n")
        
        config_file.write("!\n")
        
        # Generate route-map
        config_file.write("! Route-map for blocking China ASNs\n")
        config_file.write("route-map block_china deny 10\n")
        config_file.write(" description Block routes originated from Chinese ASNs\n")
        config_file.write(" match as-path CHINA_ASN\n")
        config_file.write("!\n")
        config_file.write("route-map block_china permit 20\n")
        config_file.write(" description Allow all other routes\n")
        config_file.write("!\n")
# ============================================================================

if __name__ == "__main__":
    asn_list = fetch_asns()
    # ========================================================================
    # MODIFIED: Added print statement
    # ========================================================================
    print(f"Fetched {len(asn_list)} ASNs from bgp.he.net")
    # ========================================================================
    
    save_asns_to_file(asn_list)
    # ========================================================================
    # MODIFIED: Added print statement
    # ========================================================================
    print("Saved ASN list to china_asns.txt")
    # ========================================================================
    
    generate_bird_config(asn_list)
    # ========================================================================
    # MODIFIED: Added print statement
    # ========================================================================
    print("Generated BIRD configuration: bird_filter.conf")
    # ========================================================================
    
    # ========================================================================
    # NEW: Generate FRR configuration
    # ========================================================================
    generate_frr_config(asn_list)
    print("Generated FRR configuration: frr_filter.conf")
    # ========================================================================
