# ASN-China

**English** | [简体中文](README.zh-CN.md)

Daily-updated list of China ASNs, plus ready-to-use BGP filter configs to **block routes originating from Chinese ASNs** on BIRD, FRR, and MikroTik RouterOS v7.

Forked from [missuo/ASN-China](https://github.com/missuo/ASN-China). This fork replaces the upstream IP lists with router-oriented filter generation.

## How it works

A single GitHub Action (**Update ASN Lists**) runs daily at 16:00 UTC (00:00 Beijing): `scripts/generate_asn_lists.py` scrapes [bgp.he.net/country/CN](https://bgp.he.net/country/CN), regenerates all four output files, and the changes are auto-committed. If the scrape returns an implausibly small list, the run aborts without touching the files.

## Files

| File | Purpose |
|------|---------|
| `china_asns.txt` | Plain list of China ASNs, one per line (~5,200 entries) |
| `bird_filter.conf` | BIRD: `china_asns` define + `block_china` filter (rejects routes whose origin AS is Chinese) |
| `frr_filter.conf` | FRR: `CHINA_ASN` as-path access-list + `block_china` route-map |
| `china_asns.rsc` | MikroTik RouterOS v7: populates the `CHINA_ASNS` `/routing/filter/num-list` |
| `update_china_asns` | RouterOS script that downloads `china_asns.rsc` and re-imports it |
| `bird.conf` | Example BIRD config wiring `block_china` into a BGP session |

Raw URLs (always latest):

```
https://raw.githubusercontent.com/ben0112/ASN-China/main/china_asns.txt
https://raw.githubusercontent.com/ben0112/ASN-China/main/bird_filter.conf
https://raw.githubusercontent.com/ben0112/ASN-China/main/frr_filter.conf
https://raw.githubusercontent.com/ben0112/ASN-China/main/china_asns.rsc
```

## Usage

### BIRD

Download `bird_filter.conf`, include it, and apply the filter on the sessions you want to protect (see `bird.conf` for a full example):

```
include "bird_filter.conf";

protocol bgp upstream {
    local as 65254;
    neighbor 192.0.2.1 as 65000;
    export filter block_china;
}
```

Reload with `birdc configure`.

### FRR

Load the as-path list and route-map, then apply the route-map to a neighbor:

```
vtysh -f frr_filter.conf

router bgp 65254
 neighbor 192.0.2.1 route-map block_china in
```

### MikroTik RouterOS v7

1. Create a script from `update_china_asns` (System → Scripts). It downloads `china_asns.rsc`, clears the `CHINA_ASNS` num-list, and re-imports it.
2. Schedule it daily:

   ```
   /system/scheduler add name=update-china-asns interval=1d start-time=03:00:00 \
       on-event="/system/script/run update_china_asns"
   ```

3. Reference the list in your routing filters, e.g.:

   ```
   /routing/filter/rule add chain=bgp-in \
       rule="if (bgp-path.last in CHINA_ASNS) { reject; }"
   ```

   Adjust the chain/rule to your setup.

## Scripts

`scripts/generate_asn_lists.py` is the single generator, run daily by CI. It scrapes the ASN list and writes all four output files: `china_asns.txt`, `bird_filter.conf`, `frr_filter.conf`, and `china_asns.rsc`.

Run locally:

```bash
pip install requests lxml
python scripts/generate_asn_lists.py
```

## Data source & caveats

- All data comes from a single HTML scrape of [bgp.he.net](https://bgp.he.net/country/CN); accuracy depends on Hurricane Electric's country attribution. If the page layout changes, the workflow fails loudly and keeps the last good lists.
- Blocking by origin AS only filters routes *originated* by Chinese ASNs — traffic transiting China or Chinese networks announcing from foreign ASNs is not covered.

## Credits

Based on [missuo/ASN-China](https://github.com/missuo/ASN-China) by [@missuo](https://github.com/missuo).
