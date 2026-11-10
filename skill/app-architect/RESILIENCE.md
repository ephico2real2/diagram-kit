# High availability, disaster recovery and the edge, by cloud

If a review covers availability, recovery or the public edge, read this file for section 6 of `SKILL.md`. Each fact
has its source. A **research item** is a point that no primary source confirmed on the date below. The review states
it as a question. A drill or the provider's page settles it before anyone builds on it.

Read on 2026-11-07. Managed offers change often, so open each link again before a recommendation depends on it.

## 1. The order of the options

The recovery point objective (RPO) is the data you can lose. The recovery time objective (RTO) is the time to serve
again. Recommend the first option that meets the RPO and the RTO of the owner. Record both numbers for each option, measured in a drill, not taken
from a data sheet.

| Order | Option | What it covers | What it costs |
| --- | --- | --- | --- |
| 1 | Zones in one region | The loss of one data center: nodes, a zone of the database | Low. Managed services do it with one setting |
| 2 | A second region of the same cloud | The loss of a region | One more copy of the platform. The same tools, identity, images and managed database, with its own replica in that region |
| 3 | A second cloud | The loss of a provider, or a rule that names a second provider | Two platforms. The database needs a copy outside each managed service, and the network between the clouds needs a VPN or an interconnect |

Option 2 is the default for disaster recovery. If a requirement names a second cloud, recommend option 3, and state
its cost in the same finding.

## 2. Cilium on each cloud

| Cloud | Cilium today | Between clusters |
| --- | --- | --- |
| Google (GKE) | GKE Dataplane V2 is built on Cilium. It is the default for new Autopilot clusters. You turn it on at the creation of a cluster, and not later. It does not support the `CiliumNetworkPolicy` and `CiliumClusterwideNetworkPolicy` APIs ([Dataplane V2](https://docs.cloud.google.com/kubernetes-engine/docs/concepts/dataplane-v2)) | Google's path is multi-cluster Services and multi-cluster Gateways in a fleet. ClusterMesh with Dataplane V2: **research item**. A third-party guide says that a self-installed Cilium needs a cluster with Dataplane V2 off ([guide](https://oneuptime.com/blog/post/2026-03-13-validate-cilium-requirements-gke/view)): **research item** |
| Microsoft (AKS) | Azure CNI Powered by Cilium: the Azure CNI control plane with the Cilium data plane, no kube-proxy, Linux only. It is the default on AKS Automatic. AKS manages the Cilium configuration, and you cannot change it. `CiliumClusterwideNetworkPolicy` is not supported ([AKS](https://learn.microsoft.com/en-us/azure/aks/azure-cni-powered-by-cilium)) | Fleet Manager cross-cluster networking is a managed ClusterMesh. It needs Azure CNI Powered by Cilium, Advanced Container Networking Services and one flat network (one virtual network, or peered ones). No overlay, up to 255 clusters, and no self-managed ClusterMesh beside it. On the date of reading it was in preview. Preview features are not for production ([Fleet](https://learn.microsoft.com/en-us/azure/kubernetes-fleet/concepts-cross-cluster-networking)) |
| Amazon (EKS) | The AWS VPC CNI is the default. AWS supports its own build of Cilium v1.17 and v1.18 for EKS Hybrid Nodes only. Source: [Hybrid Nodes](https://docs.aws.amazon.com/eks/latest/userguide/hybrid-nodes-cni.html). On standard EKS, you install Cilium yourself, chained to the VPC CNI or in its place, and you support it | Self-managed ClusterMesh. Each requirement in section 3 is yours |

So the review states, for each cloud, which Cilium the cluster gets and who supports it. A managed Cilium is easier to
operate. But on AKS the provider owns its configuration, and on GKE the Cilium APIs are reduced.

## 3. ClusterMesh: what it needs and what it does not do

From the Cilium setup page ([Cluster Mesh setup](https://docs.cilium.io/en/latest/network/clustermesh/setup/)):

- The pod address ranges (PodCIDR) of all clusters and all nodes do not overlap. Choose them before the first cluster,
  because a change later means a rebuild.
- The nodes of all clusters can reach each other, and the firewall allows the ports that the page lists. Inside one
  cloud that is peering or a transit network. Between clouds it is a VPN or an interconnect.
- In native routing mode, each cluster has a native routing CIDR that covers the pod ranges of all clusters.

For failover, a global service uses `service.cilium.io/affinity: "local"`. Traffic stays in its own cluster. If no
local backend is healthy, traffic goes to the other cluster. Source: [affinity](https://docs.cilium.io/en/stable/network/clustermesh/affinity/).
Issue [cilium#46623](https://github.com/cilium/cilium/issues/46623) reports that `affinity: "none"` drops the remote
backends. If no local backend is healthy, traffic then stops. Test the failover on the Cilium version you run.

If a cluster fails, the effect on an open connection is not in the Cilium docs: **research item**. Measure it in
the drill.

ClusterMesh moves requests between clusters. It does not copy data. Each database, queue and bucket needs its own
replication to the recovery site, and that replication sets the RPO.

## 4. The database: managed PostgreSQL across regions

| Service | How it recovers in a second region | Facts to record |
| --- | --- | --- |
| Amazon RDS for PostgreSQL | A cross-region read replica. If the main region fails, you promote the replica, and the application points to it ([AWS](https://aws.amazon.com/about-aws/whats-new/2016/06/amazon-rds-for-postgresql-now-supports-cross-region-read-replicas)) | Data transfer between regions costs extra. With no write load, the replica can lag up to 5 minutes ([AWS blog](https://aws.amazon.com/blogs/database/best-practices-for-amazon-rds-for-postgresql-cross-region-read-replicas/)). A promoted replica does not return by itself: plan the way back |
| Amazon Aurora PostgreSQL | A global database. RPO typically seconds and RTO typically minutes. A managed switchover needs the same major and minor engine version in both clusters. `rds.global_db_rpo` sets an upper limit on the RPO, but writes pause while no secondary is within it ([AWS](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-global-database-disaster-recovery.html)) | The bound on the RPO can stop writes, which is an availability cost |
| Google Cloud SQL for PostgreSQL | A cross-region replica, promoted for a regional move or for recovery ([Cloud SQL](https://docs.cloud.google.com/sql/docs/postgres/replication/cross-region-replicas)) | Lag and cost: **research item** |
| Azure Database for PostgreSQL | **Research item** | |

Across clouds, no managed service above replicates to another provider. PostgreSQL logical replication to a database
in the other cloud is the usual method, with its limits (no DDL, sequences copied by hand): **research item** for each
pair.

## 5. The edge: a CDN and a security layer

The edge is what the client reaches first. Compare the CDN of each cloud (CloudFront, Cloud CDN, Front Door) with a
CDN of its own, such as Cloudflare, and record the choice. Cloudflare is worth a spike, because one layer gives the
following, independent of the cloud behind it:

- A CDN, a web application firewall, DDoS protection and bot management.
- Load balancing across origins with health monitors. With steering off, it follows the order of the pools. That
  order gives active and passive failover between regions or clouds. Source: [Load Balancing](https://developers.cloudflare.com/load-balancing/monitors/).
  The recovery switch then does not depend on the DNS of the cloud that failed. Load balancing is a paid add-on:
  make sure that you know the price before the recommendation.
- Cloudflare Tunnel: the origin makes outbound connections to Cloudflare, so it needs no public address and no open
  inbound port ([Tunnel](https://developers.cloudflare.com/tunnel/concepts/)). Close every other path to the origin
  too. If the origin stays reachable, a client can go around Cloudflare.
- Cloudflare holds PCI DSS Level 1 service provider status for a defined set of products, among them the WAF, SSL/TLS,
  bot management, DDoS protection and logs. Source: [Trust Hub](https://www.cloudflare.com/trust-hub/compliance-resources/pci-dss/).
  The customer sets the minimum TLS version of the zone to 1.2 ([TLS compliance](https://developers.cloudflare.com/ssl/reference/compliance-and-vulnerabilities/)).

Record the costs in the same finding:

- Cloudflare ends TLS, so it reads each request. Personal data, identity documents and card data pass through it. Put
  it in the data flow diagram, the vendor list and the data processing agreement.
- The edge is now a dependency of every request. Write the bypass (DNS only, straight to the cloud load balancer) in
  the runbook, and test it in the drill.
- Mobile apps keep the API host name. If the app calls a name and not an address, a change of edge is a DNS change. It
  then needs no store release.

## 6. The drill

A recovery option is not done until a drill shows it. For each option recommended, the plan has a drill that:

1. Stops the region, the cluster or the edge on purpose, in a copy of production.
2. Measures the RTO from the first failed request to the first good one, and the RPO from the last write saved.
3. Records open connections, the queue, the scheduled jobs and the way back.
4. Saves the numbers and the commands as evidence, and repeats each quarter or after each change of the topology.
