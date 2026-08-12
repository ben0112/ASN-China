# ASN-China

[English](README.md) | **简体中文**

每日更新的中国 ASN 列表，并提供可直接用于 BIRD、FRR 和 MikroTik RouterOS v7 的 BGP 过滤器配置，用于**屏蔽源自中国 ASN 的路由**。

Fork 自 [missuo/ASN-China](https://github.com/missuo/ASN-China)。本 fork 将上游的 IP 列表替换为面向路由器的过滤器生成。

## 工作原理

单个 GitHub Action（**Update ASN Lists**）每天 16:00 UTC（北京时间 00:00）运行：`scripts/generate_asn_lists.py` 抓取 [bgp.he.net/country/CN](https://bgp.he.net/country/CN)，重新生成全部四个输出文件并自动提交。如果抓取到的列表数量异常偏少，任务会中止且不修改任何文件。

## 文件

| 文件 | 用途 |
|------|------|
| `china_asns.txt` | 纯文本中国 ASN 列表，每行一个（约 5,200 条） |
| `bird_filter.conf` | BIRD：`china_asns` 定义 + `block_china` 过滤器（拒绝源 AS 为中国的路由） |
| `frr_filter.conf` | FRR：`CHINA_ASN` as-path access-list + `block_china` route-map |
| `china_asns.rsc` | MikroTik RouterOS v7：填充 `CHINA_ASNS` `/routing/filter/num-list` |
| `update_china_asns` | RouterOS 脚本：下载 `china_asns.rsc` 并重新导入 |
| `bird.conf` | 示例 BIRD 配置，演示如何在 BGP 会话中使用 `block_china` |

Raw 地址（始终为最新版本）：

```
https://raw.githubusercontent.com/ben0112/ASN-China/main/china_asns.txt
https://raw.githubusercontent.com/ben0112/ASN-China/main/bird_filter.conf
https://raw.githubusercontent.com/ben0112/ASN-China/main/frr_filter.conf
https://raw.githubusercontent.com/ben0112/ASN-China/main/china_asns.rsc
```

## 使用方法

### BIRD

下载 `bird_filter.conf`，include 之后在需要保护的会话上应用过滤器（完整示例见 `bird.conf`）：

```
include "bird_filter.conf";

protocol bgp upstream {
    local as 65254;
    neighbor 192.0.2.1 as 65000;
    export filter block_china;
}
```

使用 `birdc configure` 重新加载。

### FRR

加载 as-path 列表和 route-map，然后将 route-map 应用到 neighbor：

```
vtysh -f frr_filter.conf

router bgp 65254
 neighbor 192.0.2.1 route-map block_china in
```

### MikroTik RouterOS v7

1. 用 `update_china_asns` 的内容创建脚本（System → Scripts）。它会下载 `china_asns.rsc`，清空 `CHINA_ASNS` num-list 并重新导入。
2. 设置每日计划任务：

   ```
   /system/scheduler add name=update-china-asns interval=1d start-time=03:00:00 \
       on-event="/system/script/run update_china_asns"
   ```

3. 在路由过滤器中引用该列表，例如：

   ```
   /routing/filter/rule add chain=bgp-in \
       rule="if (bgp-path.last in CHINA_ASNS) { reject; }"
   ```

   请根据自己的环境调整 chain 和规则。

## 脚本

`scripts/generate_asn_lists.py` 是唯一的生成器，由 CI 每日运行。它抓取 ASN 列表并写出全部四个输出文件：`china_asns.txt`、`bird_filter.conf`、`frr_filter.conf` 和 `china_asns.rsc`。

本地运行：

```bash
pip install requests lxml
python scripts/generate_asn_lists.py
```

## 数据来源与注意事项

- 所有数据来自对 [bgp.he.net](https://bgp.he.net/country/CN) 的单一 HTML 抓取，准确性取决于 Hurricane Electric 的国家归属判定。如果页面布局发生变化，工作流会显式失败并保留上一次的有效列表。
- 按源 AS 屏蔽只能过滤由中国 ASN *始发* 的路由——经中国中转的流量，以及中国网络通过国外 ASN 宣告的路由不在覆盖范围内。

## 致谢

基于 [@missuo](https://github.com/missuo) 的 [missuo/ASN-China](https://github.com/missuo/ASN-China)。
