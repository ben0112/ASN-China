# ASN-China

Daily-updated list of China ASNs, plus ready-to-use BGP filter configs to **block routes originating from Chinese ASNs** on BIRD, FRR, and MikroTik RouterOS v7.

Forked from [missuo/ASN-China](https://github.com/missuo/ASN-China). This fork replaces the upstream IP lists with router-oriented filter generation.

## How it works

Two GitHub Actions keep the files current:

1. **Update ASN and IP List** (daily at 16:00 UTC / 00:00 Beijing) — runs `scripts/BirdAndFRR.py`, which scrapes [bgp.he.net/country/CN](https://bgp.he.net/country/CN) and regenerates `china_asns.txt`, `bird_filter.conf`, and `frr_filter.conf`.
2. **Update CHINA_ASNS RSC** (daily at 18:00 UTC) — converts `china_asns.txt` into `china_asns.rsc` for MikroTik.

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

`scripts/BirdAndFRR.py` is the single generator, run daily by CI. It scrapes the ASN list and writes `china_asns.txt`, `bird_filter.conf`, and `frr_filter.conf`.

Run locally:

```bash
pip install requests lxml
python scripts/BirdAndFRR.py
```

## Data source & caveats

- All data comes from a single HTML scrape of [bgp.he.net](https://bgp.he.net/country/CN). If the page layout changes, updates will silently stop; accuracy depends on Hurricane Electric's country attribution.
- Blocking by origin AS only filters routes *originated* by Chinese ASNs — traffic transiting China or Chinese networks announcing from foreign ASNs is not covered.

## Credits

Based on [missuo/ASN-China](https://github.com/missuo/ASN-China) by [@missuo](https://github.com/missuo).
