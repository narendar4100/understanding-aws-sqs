import json
from pathlib import Path

import build_pages as bp

ROOT = Path(__file__).resolve().parent / "frontend"
DOCS_NOTE = "Confirm the current official page before treating a price or quota as final."


def iam():
    return {
        "id": "iam", "depth": 1, "path": "iam/index.html",
        "title": "AWS IAM Reference &amp; Live Labs",
        "description": "IAM evaluation order, roles, policies, limits, cost, alternatives, and exam drills.",
        "accent": "text-amber-400",
        "eyebrow": "AWS Identity and Access Management",
        "headline": "Every call is allowed only after every guard says yes",
        "lede": "IAM answers one question: may this principal call this action on this resource? Users, groups, and roles do not become powerful because they exist. A policy has to allow the call, and no applicable policy may deny it.",
        "diagram": [("users", "Principal", "user or role"), ("iam", "IAM", "evaluates"), ("s3", "Resource", "allows or denies")],
        "jumps": bp.JUMPS,
        "summary_title": "Learn the evaluation order before memorizing service names",
        "summary": "An explicit deny wins everywhere. Permission boundaries, service control policies, and session policies never grant access; they only limit it. In the same account, an identity policy or a resource policy can allow a call. Across accounts, both sides normally must allow it. A role also needs a trust policy before anyone can assume it.",
        "bad_title": "One admin key shared by every Lambda",
        "bad": [
            "A long-lived access key is baked into the deployment package.",
            "Billing and shipping can delete each other's data because they share AdministratorAccess.",
            "A leaked key remains valid until a person remembers to disable it.",
        ],
        "good_title": "One role per workload, scoped to its ARNs",
        "good": [
            "Lambda assumes a role and receives temporary credentials from STS.",
            "The accept role can write one S3 prefix and put one EventBridge event.",
            "The billing role can read receipts and consume one queue. It cannot assume the shipping role.",
        ],
        "compare_title": "Which control grants access, and which control only limits it?",
        "compare_headers": ["Control", "Can it grant?", "Exam decision"],
        "compare_rows": [
            ["Identity-based policy", "Yes", "Attach it to a user, group, or role. This is the normal workload permission."],
            ["Resource-based policy", "Yes", "Required together with the identity policy for most cross-account access. In the same account it can allow a principal on its own."],
            ["Trust policy", "Assume only", "Controls who can call sts:AssumeRole. It does not allow S3 or SQS actions."],
            ["Permission boundary", "No", "Sets the maximum an identity can receive. The identity still needs an Allow."],
            ["Service control policy", "No", "Sets the maximum for an Organizations account. It does not give a user a permission."],
            ["Session policy", "No", "Shrinks one role session. Useful when a broker assumes a broad role for a narrower job."],
        ],
        "extra": '''<section class="mt-12 rounded-2xl border border-slate-800 bg-slate-900 p-6 sm:p-8">
          <p class="text-[11px] font-medium uppercase tracking-[0.18em] text-amber-400">Operations</p>
          <h2 class="mt-2 text-2xl font-semibold text-white">Use roles for compute and short-lived credentials for people</h2>
          <div class="mt-6 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <article class="rounded-xl bg-slate-950 p-5"><h3 class="font-semibold">Workforce</h3><p class="mt-2 text-sm leading-6 text-slate-400">Federation or IAM Identity Center gives temporary console access. Do not create an IAM user per employee when a central identity provider exists.</p></article>
            <article class="rounded-xl bg-slate-950 p-5"><h3 class="font-semibold">Compute</h3><p class="mt-2 text-sm leading-6 text-slate-400">EC2, Lambda, and ECS use roles. An instance profile is how an EC2 instance receives its role.</p></article>
            <article class="rounded-xl bg-slate-950 p-5"><h3 class="font-semibold">Partners</h3><p class="mt-2 text-sm leading-6 text-slate-400">Give a partner a role to assume. Require an external ID so the partner cannot be tricked into acting on the wrong account.</p></article>
            <article class="rounded-xl bg-slate-950 p-5"><h3 class="font-semibold">Evidence</h3><p class="mt-2 text-sm leading-6 text-slate-400">CloudTrail records the IAM calls. Access Analyzer finds policies that grant broader access than intended.</p></article>
          </div>
        </section>''',
        "best_title": "Five authorization decisions, predicted before the explanation",
        "best": "Give students the five live cases below and no notes. A pass is five correct decisions plus one sentence naming the winning control: implicit deny, explicit deny, same-account resource policy, cross-account missing allow, or SCP. This single lab covers the IAM questions that appear on Cloud Practitioner, Solutions Architect, Developer, and SysOps exams.",
        "lab_title": "Will this API call be allowed?",
        "lab_lede": "Read the caller, action, and policies. Choose Allow or Deny. The evaluator then names the rule that decided it.",
        "will_not": [
            "IAM does not sign in the customers of your application. That is Amazon Cognito or your own identity provider.",
            "A permission boundary or SCP with Allow does not give that permission to a user.",
            "Groups cannot contain other groups or roles. A Lambda function cannot be placed in an IAM group.",
            "IAM does not encrypt the object. KMS and the service's encryption setting do that.",
            "Deleting a user does not delete the resources that user created.",
        ],
        "limits": [
            ["Policy evaluation", "Explicit deny beats every allow", "The most common IAM question. Find the deny first."],
            ["Role credentials", "Temporary STS credentials, not an access key on the role", "Choose a role for EC2 or Lambda, not a stored key."],
            ["Groups", "A user can be in multiple groups; groups do not nest", "A design that puts a role in a group is invalid."],
            ["Policy size", "Customer managed policies have a documented character maximum", "Split a huge policy by workload rather than attaching AdministratorAccess."],
            ["Session length", "Role sessions have a maximum duration, up to 12 hours", "Long-lived keys are the wrong fix for a long batch job."],
            ["Scope", "IAM is global; most resource ARNs are regional", "A policy can name a region. A role does not live in one region."],
        ],
        "cost_title": "Users, groups, roles, and policies have no IAM charge",
        "cost_points": [
            "Standard IAM identities and policies are not a separate bill line.",
            "You still pay for the services the principal calls, for KMS requests, and for CloudTrail if you retain data events.",
            "Identity Center and external identity products can have their own pricing. Do not describe those as an IAM API fee.",
        ],
        "cost_example": f"<strong class=\"text-white\">Example:</strong> five Lambda roles and twenty scoped policies add no IAM identity charge. The bill appears when those roles call S3, SQS, KMS, or CloudWatch. {DOCS_NOTE}",
        "alt_title": "Pick the identity tool that matches the caller",
        "alternatives": [
            ["Employee console access", "IAM Identity Center", "Central workforce identities and temporary permission sets."],
            ["Application customers", "Amazon Cognito or an external IdP", "IAM users are a poor directory for millions of customers."],
            ["EC2, Lambda, ECS calls", "IAM role", "Temporary credentials rotate without a secret in the image."],
            ["Another AWS account", "Cross-account role plus resource policy", "Do not share the root user or a long-lived key."],
            ["Microsoft or other enterprise login", "SAML or OIDC federation", "Keep one source of employee truth."],
        ],
        "waf": [
            ["Operational Excellence", "Policies live in code and are reviewed like application changes.", "Terraform or CloudFormation diff"],
            ["Security", "Least privilege, no long-lived keys on compute, MFA for humans, external IDs for partners.", "IAM Access Analyzer"],
            ["Reliability", "Workloads use roles, so a person leaving the company does not break the service.", "No embedded keys"],
            ["Performance Efficiency", "Authorization choices do not require a central server you operate.", "STS assume-role latency is low"],
            ["Cost Optimization", "Scope permissions and avoid overpowered shared roles that force broad audit work.", "One role per function"],
            ["Sustainability", "Smaller blast radius means fewer emergency rotations and less wasted retry traffic.", "CloudTrail plus alerts"],
        ],
        "drills": [
            ["A role has s3:GetObject Allow, and the same role has s3:* Deny. Can it read an object?", "Deny. An explicit deny overrides the allow."],
            ["An SCP allows s3:PutObject. The user has no identity policy. Can the user write?", "Deny. An SCP does not grant. The user still needs an allowing identity or resource policy."],
            ["A Lambda function should read one bucket. The team suggests an IAM user and an access key in an environment variable. What do you choose?", "An execution role with s3:GetObject on that bucket ARN. The function receives temporary credentials."],
            ["Account B must read a bucket in account A. The bucket policy allows the role, but the role has no S3 allow. What happens?", "Deny. Cross-account access needs an allow on both the identity policy and the resource policy, and no explicit deny."],
            ["A permission boundary includes only S3. An administrator attaches an EC2 full-access policy to the same role. Can the role start an instance?", "No. The boundary is the maximum. EC2 actions are outside it, so they are denied."],
        ],
        "docs": [
            ("IAM User Guide", "https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html"),
            ("policy evaluation", "https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html"),
            ("IAM pricing", "https://aws.amazon.com/iam/pricing/"),
        ],
        "cases": [
            {"prompt": "The billing role has Allow s3:GetObject on arn:aws:s3:::northline-receipts/*. It calls GetObject on orders/1042.pdf. No deny exists.", "detail": "Same account. Identity policy matches the object ARN.", "options": ["Allow", "Deny"], "answer": 0, "why": "An identity Allow with no explicit deny permits the call. A same-account bucket policy is not also required."},
            {"prompt": "The same role calls s3:DeleteBucket. Its policy lists only s3:GetObject.", "detail": "There is no Deny statement and no DeleteBucket Allow.", "options": ["Allow", "Deny"], "answer": 1, "why": "IAM starts from implicit deny. No matching Allow means Deny."},
            {"prompt": "A managed policy allows s3:*. An inline policy on the same role denies s3:DeleteObject. The role deletes a receipt.", "detail": "Both policies are attached to the caller.", "options": ["Allow", "Deny"], "answer": 1, "why": "Explicit deny wins over the broad allow."},
            {"prompt": "A bucket policy in this account allows the shipping role s3:GetObject. The role's identity policies do not mention S3. It reads an object.", "detail": "Same account. There is no SCP, boundary, or explicit deny.", "options": ["Allow", "Deny"], "answer": 0, "why": "In the same account, a resource policy can allow a principal without a matching identity Allow."},
            {"prompt": "Account B's role is allowed by account A's bucket policy. The role in B has no S3 permission. It tries to read.", "detail": "Cross-account request. No explicit deny.", "options": ["Allow", "Deny"], "answer": 1, "why": "Cross-account access needs Allow on both sides. The resource policy alone is not enough."},
            {"prompt": "The identity policy allows s3:PutObject. The account SCP denies s3:PutObject. A user uploads a file.", "detail": "Organizations SCP is attached to the account.", "options": ["Allow", "Deny"], "answer": 1, "why": "An SCP deny cannot be overridden by an identity policy."},
        ],
    }


def vpc():
    return {
        "id": "vpc", "depth": 1, "path": "vpc/index.html",
        "title": "Amazon VPC Reference &amp; Live Labs",
        "description": "VPC routes, security groups, NACLs, NAT, endpoints, limits, cost, and exam drills.",
        "accent": "text-sky-400",
        "eyebrow": "Amazon Virtual Private Cloud",
        "headline": "A private network only goes where its routes and firewalls agree",
        "lede": "A VPC is your network boundary in a Region. Subnets place workloads in Availability Zones. Route tables decide the next hop, security groups remember the connection, and network ACLs do not.",
        "diagram": [("vpc", "VPC", "your CIDR"), ("users", "Subnet", "one AZ"), ("ok", "Route", "next hop")],
        "jumps": bp.JUMPS,
        "summary_title": "Draw the packet path before you add a service",
        "summary": "Public means a route to an internet gateway and a public IP, not merely a subnet named public. Private outbound internet access needs a NAT gateway or NAT instance in a public subnet. S3 and DynamoDB can skip NAT through a gateway endpoint. SQS, SNS, EventBridge, and most other services need an interface endpoint or another network path.",
        "bad_title": "Private workers with a route to nowhere",
        "bad": [
            "Lambda is attached to a private subnet and then expected to call public AWS APIs.",
            "The route table has only the local VPC route.",
            "A NAT gateway is placed in the private subnet, so it has no path to the internet either.",
        ],
        "good_title": "Public entry, private work, and the cheapest private AWS path",
        "good": [
            "Only the load balancer or API edge is public.",
            "Workers use private subnets across at least two Availability Zones.",
            "S3 uses a gateway endpoint. Other AWS APIs use interface endpoints when the workers must stay off the internet.",
        ],
        "compare_title": "Security groups and network ACLs are not substitutes",
        "compare_headers": ["Behavior", "Security group", "Network ACL"],
        "compare_rows": [
            ["State", "Stateful. Return traffic is allowed automatically.", "Stateless. Return traffic needs its own rule, usually an ephemeral port."],
            ["Attachment", "Elastic network interfaces and many AWS resources.", "A subnet."],
            ["Default custom object", "Custom group denies inbound and allows outbound.", "Custom ACL denies traffic until you add rules."],
            ["Rule style", "Allow rules.", "Allow and deny rules, evaluated by rule number."],
            ["Exam trap", "It does not block the response to an allowed request.", "Allowing inbound 443 and forgetting ephemeral outbound makes the handshake fail."],
        ],
        "extra": '''<section class="mt-12 rounded-2xl border border-slate-800 bg-slate-900 p-6 sm:p-8">
          <p class="text-[11px] font-medium uppercase tracking-[0.18em] text-sky-400">Path choice</p>
          <h2 class="mt-2 text-2xl font-semibold text-white">Use the cheapest path that meets the trust boundary</h2>
          <div class="mt-6 grid gap-4 md:grid-cols-3">
            <article class="rounded-xl bg-slate-950 p-5"><h3 class="font-semibold text-sky-300">Internet gateway</h3><p class="mt-2 text-sm leading-6 text-slate-400">Inbound and outbound for resources that have a public address. One internet gateway attaches to one VPC.</p></article>
            <article class="rounded-xl bg-slate-950 p-5"><h3 class="font-semibold text-amber-300">NAT gateway</h3><p class="mt-2 text-sm leading-6 text-slate-400">Outbound only, from private subnets. Put it in a public subnet and point the private default route at it. It has an hourly and data charge.</p></article>
            <article class="rounded-xl bg-slate-950 p-5"><h3 class="font-semibold text-emerald-300">Gateway endpoint</h3><p class="mt-2 text-sm leading-6 text-slate-400">S3 and DynamoDB. Add the prefix-list route. There is no hourly endpoint charge and traffic stays on the AWS network.</p></article>
          </div>
        </section>''',
        "best_title": "Four packet paths and one NACL trap",
        "best": "Students predict success or failure for a public web request, a private subnet with no default route, private outbound through NAT, S3 through a gateway endpoint, and a NACL that allows 443 but not ephemeral return ports. Passing means they can say which hop failed: route, security group, or NACL.",
        "lab_title": "Does this connection succeed?",
        "lab_lede": "Trace the route table first, then the security group, then the network ACL. Choose Succeeds or Fails.",
        "will_not": [
            "A VPC does not automatically give private subnets access to the internet.",
            "VPC peering is not transitive. A can peer with B and B with C without giving A a path to C.",
            "A security group alone does not create a route.",
            "A gateway endpoint does not serve SQS, SNS, Lambda, or EventBridge. Those use interface endpoints or another path.",
            "Putting a workload in a VPC does not encrypt its data.",
        ],
        "limits": [
            ["CIDR", "A VPC CIDR is chosen from the allowed private range and can later gain secondary CIDRs", "Overlapping CIDRs cannot be peered."],
            ["Reserved addresses", "The first four addresses and the last address of a subnet are reserved", "A /28 does not give you 16 usable hosts."],
            ["Internet gateway", "One internet gateway is attached to one VPC", "You do not add a second IGW to make a subnet public."],
            ["Availability", "One subnet is in one Availability Zone", "High availability needs subnets in at least two AZs."],
            ["Peering", "Routes are required on both sides, and peering is not transitive", "A hub-and-spoke design of many peers needs a transit gateway or explicit routes."],
            ["Default quotas", "VPCs, peering connections, and rules have regional quotas", "A design that needs more is a quota request, not a new account by default."],
        ],
        "cost_title": "The VPC is inexpensive until NAT or interface endpoints stay on",
        "cost_points": [
            "Creating a VPC, subnet, route table, internet gateway, security group, or gateway endpoint has no hourly network fee.",
            "A NAT gateway bills for every hour it exists and for data processed. One per AZ improves availability and multiplies the hourly charge.",
            "Interface endpoints bill hourly per AZ plus data processing. Use them when private access is a requirement, not as a default for every service.",
        ],
        "cost_example": f"<strong class=\"text-white\">Example:</strong> a student account that runs for a week with one NAT gateway can cost more than all of the SQS and SNS labs combined. Northline and Clearfile therefore teach the private design and use gateway endpoints for S3, without requiring a NAT gateway in the class account. {DOCS_NOTE}",
        "alt_title": "Choose the network feature for the path you actually need",
        "alternatives": [
            ["Public website", "Public subnets plus an internet gateway", "Clients on the internet need a public entry."],
            ["Private outbound patching", "NAT gateway", "Instances can start connections out; the internet cannot start connections in."],
            ["Private S3 or DynamoDB", "Gateway endpoint", "No NAT hourly charge for that traffic."],
            ["Private SQS, SNS, or EventBridge", "Interface endpoint", "PrivateLink into that service, with an endpoint policy."],
            ["Many VPCs in a hub", "Transit Gateway", "Peering does not provide transitive routing."],
            ["Only two VPCs", "VPC peering", "Simple and not transitive. Watch for overlapping CIDRs."],
        ],
        "waf": [
            ["Operational Excellence", "Network is code: subnets, routes, and endpoint policies are reviewed.", "Route table diff"],
            ["Security", "Least-privilege security groups, private admin paths, and flow logs.", "VPC Flow Logs"],
            ["Reliability", "Subnets and NAT or endpoints in more than one AZ.", "AZ map"],
            ["Performance Efficiency", "Traffic to S3 stays in the Region through a gateway endpoint.", "Prefix-list route"],
            ["Cost Optimization", "Avoid a NAT gateway when a gateway endpoint solves the path.", "NAT hours"],
            ["Sustainability", "Keep private workloads from polling the internet when an AWS endpoint exists.", "Endpoint metrics"],
        ],
        "drills": [
            ["A subnet is named private, but its route table sends 0.0.0.0/0 to an internet gateway and the instance has a public IP. Is it private?", "No. The route and public address make the instance reachable from the internet if the firewalls allow it."],
            ["A NACL allows inbound TCP 443 and denies everything else. Clients connect to a web server and then hang. Why?", "NACLs are stateless. The return traffic uses ephemeral ports and needs an outbound allow."],
            ["Two VPCs are peered. Only one route table has the peering route. Does the ping work?", "No. Peering needs a route on both sides, plus security group or NACL permission."],
            ["A private instance must read S3, and the company refuses a NAT gateway. What do you add?", "A gateway VPC endpoint for S3 and a route for the S3 prefix list."],
            ["VPC A peers with B, and B peers with C. Can A reach C through B?", "No. VPC peering is not transitive. Use Transit Gateway or peer A to C directly."],
        ],
        "docs": [
            ("VPC User Guide", "https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html"),
            ("security groups and NACLs", "https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Security.html"),
            ("VPC pricing", "https://aws.amazon.com/vpc/pricing/"),
        ],
        "cases": [
            {"prompt": "A web instance is in a subnet whose default route is the internet gateway. It has a public IP. The security group allows TCP 443, and both NACL directions allow the required ports.", "detail": "Client on the internet opens HTTPS.", "options": ["Succeeds", "Fails"], "answer": 0, "why": "The route, public address, security group, and NACL all agree."},
            {"prompt": "A private instance has only the local VPC route. It tries to download a public package.", "detail": "No NAT and no internet gateway route.", "options": ["Succeeds", "Fails"], "answer": 1, "why": "The route table has no next hop for the public address. The packet is dropped."},
            {"prompt": "A private subnet sends 0.0.0.0/0 to a NAT gateway in a public subnet. The NAT subnet sends 0.0.0.0/0 to the internet gateway. Security groups allow outbound.", "detail": "The instance starts the connection. It has no public IP.", "options": ["Succeeds", "Fails"], "answer": 0, "why": "NAT provides outbound-only internet access. Inbound connections from the internet still fail because the instance has no public path."},
            {"prompt": "The same private subnet has no NAT. It has a gateway endpoint route for S3. The application reads an object.", "detail": "The S3 call uses the gateway endpoint, not the public internet.", "options": ["Succeeds", "Fails"], "answer": 0, "why": "Gateway endpoints give private access to S3 without a NAT gateway."},
            {"prompt": "The security group allows 443. The NACL allows inbound 443 and has no outbound ephemeral allow. A client starts HTTPS.", "detail": "Custom NACL, stateless rules.", "options": ["Succeeds", "Fails"], "answer": 1, "why": "The response packet is a separate NACL evaluation. Missing ephemeral ports fail the handshake."},
            {"prompt": "A private worker uses the S3 gateway endpoint and then calls SQS through the same endpoint.", "detail": "The endpoint prefix list is for S3 only.", "options": ["Succeeds", "Fails"], "answer": 1, "why": "SQS is not a gateway-endpoint service. It needs an interface endpoint, NAT, or another network path."},
        ],
    }


def s3():
    return {
        "id": "s3", "depth": 1, "path": "s3/index.html",
        "title": "Amazon S3 Reference &amp; Live Labs",
        "description": "S3 storage classes, consistency, security, limits, cost, alternatives, and exam drills.",
        "accent": "text-green-400",
        "eyebrow": "Amazon Simple Storage Service",
        "headline": "A private object store with a class for each access pattern",
        "lede": "S3 stores objects in buckets. You choose a storage class for how often the object is read, how fast it must return, and whether it can live in one Availability Zone. Security is a bucket boundary, not a folder permission.",
        "diagram": [("users", "Client", "puts an object"), ("iam", "IAM", "authorizes"), ("s3", "Bucket", "stores it")],
        "jumps": bp.JUMPS,
        "summary_title": "Separate durability, availability, and access frequency",
        "summary": "S3 Standard is designed for eleven nines of durability across multiple Availability Zones. A storage class does not change ownership or encryption. Current S3 provides strong consistency for create, overwrite, delete, and list. Block Public Access can override a bucket policy that would otherwise make an object public.",
        "bad_title": "A public bucket used as an application disk",
        "bad": [
            "A bucket policy allows s3:GetObject for everyone so a website can preview receipts.",
            "Every object stays in S3 Standard for seven years, including records nobody reads.",
            "The application lists the whole bucket to find one order.",
        ],
        "good_title": "Private objects, explicit prefixes, and a lifecycle",
        "good": [
            "Block Public Access stays on. Callers use IAM or a short-lived presigned URL.",
            "Receipts use Standard or Intelligent-Tiering. Seven-year records transition to a Glacier class.",
            "The application stores the object key in its database and gets that key directly.",
        ],
        "compare_title": "Choose the class from the retrieval promise",
        "compare_headers": ["Class", "Retrieval", "Exam clue"],
        "compare_rows": [
            ["S3 Standard", "Milliseconds, frequent access", "Active content and current receipts."],
            ["Intelligent-Tiering", "Automatic, small monitoring fee", "Unknown or changing access pattern. No retrieval fee."],
            ["Standard-IA and One Zone-IA", "Milliseconds, retrieval fee", "Infrequent reads. One Zone-IA can be lost with that AZ and is only for rebuildable data."],
            ["Glacier Instant Retrieval", "Milliseconds, archive price", "Rare reads that still need immediate access."],
            ["Glacier Flexible Retrieval", "Minutes to hours", "Archives that can wait. Minimum storage duration applies."],
            ["Glacier Deep Archive", "Hours by default", "Lowest storage price and the longest wait. Common compliance choice."],
        ],
        "extra": '''<section class="mt-12 rounded-2xl border border-slate-800 bg-slate-900 p-6 sm:p-8">
          <p class="text-[11px] font-medium uppercase tracking-[0.18em] text-green-400">Controls that exams combine</p>
          <h2 class="mt-2 text-2xl font-semibold text-white">Encryption, versioning, and public access solve different problems</h2>
          <div class="mt-6 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <article class="rounded-xl bg-slate-950 p-5"><h3 class="font-semibold">Block Public Access</h3><p class="mt-2 text-sm leading-6 text-slate-400">Account or bucket settings can block a public ACL or policy even if someone adds one later.</p></article>
            <article class="rounded-xl bg-slate-950 p-5"><h3 class="font-semibold">Versioning</h3><p class="mt-2 text-sm leading-6 text-slate-400">Required for replication. Delete becomes a delete marker. MFA Delete is a separate versioning control.</p></article>
            <article class="rounded-xl bg-slate-950 p-5"><h3 class="font-semibold">Object Lock</h3><p class="mt-2 text-sm leading-6 text-slate-400">Governance mode can be overridden by a special permission. Compliance mode cannot be shortened, even by the root user, until retention ends.</p></article>
            <article class="rounded-xl bg-slate-950 p-5"><h3 class="font-semibold">Encryption</h3><p class="mt-2 text-sm leading-6 text-slate-400">SSE-S3, SSE-KMS, or a customer-provided key. A presigned URL still obeys the signer's IAM permission.</p></article>
          </div>
        </section>''',
        "best_title": "Pick the class, then decide whether the object can be public",
        "best": "Use four objects: a hot product image, an unknown-access log, a seven-year contract, and a rebuildable thumbnail. Then ask what happens when a bucket policy grants public read while Block Public Access is on. Students should leave able to reject One Zone-IA for the only copy of a contract and reject a public bucket for receipts.",
        "lab_title": "Which storage and access decision fits?",
        "lab_lede": "Choose the answer that satisfies durability, retrieval time, and cost. Do not choose a cheaper class that breaks the retrieval promise.",
        "will_not": [
            "S3 is not a file system and is not a relational database. Prefixes are key names, not POSIX folders.",
            "S3 does not move objects between classes unless Intelligent-Tiering or a lifecycle rule is configured.",
            "The S3 website endpoint does not provide HTTPS. Put CloudFront in front when browsers need TLS.",
            "A presigned URL cannot grant more permission than the signer has, and it stays valid until it expires.",
            "Replication does not start unless versioning is enabled. Existing objects are not copied unless you ask for them.",
        ],
        "limits": [
            ["Object size", "Up to 5 TB. A single PUT is limited to 5 GB.", "Above 5 GB, multipart upload is required. It is recommended well before that."],
            ["Consistency", "Strong consistency for PUT, overwrite, DELETE, and list", "An answer that says overwrites are eventually consistent is outdated."],
            ["Request pattern", "High request rates are spread across prefixes", "A single hot key is an application problem. Store the key; do not list the bucket."],
            ["Bucket names", "Globally unique, DNS-compatible, no uppercase", "Buckets are regional resources with a global name."],
            ["Minimum duration", "Several IA and Glacier classes charge a minimum storage time", "Transitioning data you delete tomorrow can cost more."],
            ["Public access", "Block Public Access overrides a public ACL or policy", "A later bucket policy does not make the account public when the block remains."],
        ],
        "cost_title": "Storage, requests, retrieval, and transfer are separate",
        "cost_points": [
            "Standard charges mainly for storage and requests. Infrequent classes add a retrieval fee and a minimum duration.",
            "Lifecycle transitions and early deletes can have their own charges.",
            "Cross-Region replication adds storage in the destination and data transfer.",
            "SSE-KMS adds KMS request charges. SSE-S3 does not add a KMS key charge.",
        ],
        "cost_example": f"<strong class=\"text-white\">Example:</strong> a 200 KB receipt read thousands of times per day belongs in Standard or Intelligent-Tiering. The same object stored in Glacier Flexible Retrieval would save storage and then spend the savings on retrieval delays and fees. {DOCS_NOTE}",
        "alt_title": "Use S3 for objects, not for every byte",
        "alternatives": [
            ["Shared file system for a server", "Amazon EFS or FSx", "POSIX-style file access and locking."],
            ["Disk for one instance", "Amazon EBS", "Block storage attached to a compute instance."],
            ["Small high-frequency records", "DynamoDB", "Key-value queries and single-digit millisecond reads."],
            ["Query files in place", "Amazon Athena over S3", "SQL on objects without loading them into a database first."],
            ["Global low-latency website", "S3 plus CloudFront", "The bucket stays private where possible; the CDN serves cached content."],
        ],
        "waf": [
            ["Operational Excellence", "Lifecycle rules and inventory are visible as code.", "Lifecycle configuration"],
            ["Security", "Block Public Access, least-privilege bucket policy, encryption, and access logs.", "Public access block"],
            ["Reliability", "Versioning, cross-Region replication where the business needs it, and multi-AZ classes for primary data.", "Replication role"],
            ["Performance Efficiency", "Multipart uploads and direct key access.", "Object key stored by the app"],
            ["Cost Optimization", "Class and lifecycle match the real retrieval pattern.", "Storage lens or inventory"],
            ["Sustainability", "Cold data moves out of a hot class. Incomplete multipart uploads expire.", "Abort incomplete uploads"],
        ],
        "drills": [
            ["A bucket policy allows public GetObject. Block Public Access is enabled for public policies. Can an anonymous user read?", "No. Block Public Access wins over that public policy."],
            ["The only copy of a contract must survive an Availability Zone loss. Which cheaper class is unacceptable?", "S3 One Zone-IA. It stores data in one AZ."],
            ["A team wants HTTPS on the S3 static website endpoint. What do you add?", "Amazon CloudFront, or serve the site through another HTTPS endpoint. The S3 website endpoint itself does not terminate HTTPS."],
            ["Cross-Region replication is configured, but versioning is off on the source. What is missing?", "Versioning must be enabled on the source and destination."],
            ["An object is overwritten and another reader fetches it immediately. What consistency should they expect?", "Strong consistency. They should see the latest overwrite or delete."],
        ],
        "docs": [
            ("S3 User Guide", "https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html"),
            ("storage classes", "https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-class-intro.html"),
            ("S3 pricing", "https://aws.amazon.com/s3/pricing/"),
        ],
        "cases": [
            {"prompt": "Product photos are read on nearly every page view. They must survive an AZ loss.", "detail": "Frequent access. Primary copy.", "options": ["S3 Standard", "Glacier Deep Archive", "S3 One Zone-IA"], "answer": 0, "why": "Frequent reads belong in Standard. Deep Archive adds hours of retrieval. One Zone-IA risks the only copy."},
            {"prompt": "Application logs might be read tomorrow or not for six months. You do not want to guess the tier.", "detail": "Unknown access pattern.", "options": ["S3 Intelligent-Tiering", "Glacier Flexible Retrieval", "Standard-IA immediately"], "answer": 0, "why": "Intelligent-Tiering moves objects automatically and has no retrieval fee. A Glacier class is a poor fit when someone may need the log immediately."},
            {"prompt": "Compliance keeps invoices for seven years. A restore measured in hours is acceptable, and reads are rare.", "detail": "Lowest storage cost is the goal.", "options": ["S3 Standard", "S3 Glacier Deep Archive", "S3 One Zone-IA"], "answer": 1, "why": "Deep Archive matches rare reads and a long restore. One Zone-IA is the wrong durability choice for a compliance original."},
            {"prompt": "Thumbnails can be rebuilt from the original. The business accepts one-AZ risk to cut cost.", "detail": "Infrequent reads, rebuildable.", "options": ["S3 One Zone-IA", "S3 Standard for every thumbnail forever", "Object Lock compliance"], "answer": 0, "why": "One Zone-IA is the exam answer for noncritical, rebuildable, infrequent data. Object Lock is a retention control, not a storage class."},
            {"prompt": "A bucket policy grants Principal * s3:GetObject. Block Public Access for bucket policies is on. Can the internet read the receipt?", "detail": "Anonymous HTTPS GET.", "options": ["Public can read", "Public is blocked"], "answer": 1, "why": "Block Public Access overrides the public bucket policy. Callers still need a permitted IAM principal or a valid presigned URL."},
        ],
    }


def lambda_page():
    return {
        "id": "lambda", "depth": 1, "path": "lambda/index.html",
        "title": "AWS Lambda Reference &amp; Live Labs",
        "description": "Lambda invocation models, concurrency, VPC behavior, limits, cost, alternatives, and exam drills.",
        "accent": "text-orange-400",
        "eyebrow": "AWS Lambda",
        "headline": "Run the function, then get out of the way",
        "lede": "Lambda runs code without a server to patch. The exam turns on how the event arrives: a caller waiting for a response, an asynchronous event, or a poller reading a stream or queue. Concurrency is an account pool, not an infinite setting.",
        "diagram": [("apigw", "Caller", "API or event"), ("lambda", "Function", "one invocation"), ("iam", "Role", "temporary rights")],
        "jumps": bp.JUMPS,
        "summary_title": "Name the invocation model before you tune retries",
        "summary": "API Gateway and an Application Load Balancer invoke Lambda synchronously. S3 notifications, SNS, and EventBridge invoke it asynchronously, and asynchronous calls retry twice before a destination or DLQ. SQS, Kinesis, and DynamoDB streams use an event source mapping: Lambda polls, and the queue or stream controls the retry. Reserved concurrency of zero throttles every call.",
        "bad_title": "A 15-minute API request and one shared admin role",
        "bad": [
            "The browser waits on Lambda while a report is built.",
            "Reserved concurrency is left at the account default, so one busy function consumes the pool.",
            "The function is attached to a private subnet and then cannot reach S3.",
        ],
        "good_title": "A short accept path and a buffered worker",
        "good": [
            "The API function validates, stores the receipt, publishes the event, and returns.",
            "The worker has its own role and a reserved concurrency cap.",
            "If the worker joins a VPC, S3 is reached through a gateway endpoint or another explicit path.",
        ],
        "compare_title": "The caller, the retry, and the timeout are a set",
        "compare_headers": ["Source", "Model", "What students must say"],
        "compare_rows": [
            ["API Gateway or ALB", "Synchronous", "The caller waits. API Gateway REST integrations time out at 29 seconds, even though Lambda can run for 15 minutes."],
            ["SNS, S3, EventBridge", "Asynchronous", "Lambda retries twice. Then use an on-failure destination or DLQ."],
            ["SQS", "Event source mapping", "A poller receives batches. Failed messages return to the queue; maxReceiveCount moves them to the SQS DLQ."],
            ["Kinesis or DynamoDB streams", "Event source mapping", "Order is per shard or partition. A poison record can block that shard until it expires or is handled."],
            ["Reserved concurrency", "Account pool", "It caps the function and removes that amount from the unreserved pool. Zero disables the function."],
            ["Provisioned concurrency", "Prepared environments", "It reduces cold starts and costs money while idle. It is allocated from reserved concurrency."],
        ],
        "extra": '''<section class="mt-12 rounded-2xl border border-slate-800 bg-slate-900 p-6 sm:p-8">
          <p class="text-[11px] font-medium uppercase tracking-[0.18em] text-orange-400">Concurrency calculator</p>
          <h2 class="mt-2 text-2xl font-semibold text-white">A reserved cap does not borrow unused account concurrency</h2>
          <div class="mt-6 grid gap-4 md:grid-cols-3">
            <label class="text-sm text-slate-300">Reserved concurrency<input id="reserved" class="mt-2 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 font-mono text-white" type="number" min="0" value="20" /></label>
            <label class="text-sm text-slate-300">Simultaneous arrivals<input id="burst" class="mt-2 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 font-mono text-white" type="number" min="1" value="80" /></label>
            <button id="calc" type="button" class="self-end rounded-lg bg-orange-500 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-orange-400">Calculate</button>
          </div>
          <p id="calc-out" class="mt-4 text-sm leading-6 text-slate-300" aria-live="polite">Set a cap and calculate. Try zero last.</p>
        </section>''',
        "extra_script": '''
    const calc = document.getElementById("calc");
    if (calc) {
      calc.addEventListener("click", () => {
        const reserved = Number(document.getElementById("reserved").value);
        const burst = Number(document.getElementById("burst").value);
        const out = document.getElementById("calc-out");
        if (!Number.isFinite(reserved) || !Number.isFinite(burst) || reserved < 0 || burst < 1) {
          out.textContent = "Enter a reserved concurrency of 0 or more and a burst of at least 1.";
          return;
        }
        if (reserved === 0) {
          out.textContent = "Reserved concurrency of 0 throttles every invocation. This function cannot borrow the unreserved account pool.";
          return;
        }
        const started = Math.min(burst, reserved);
        out.textContent = started + " invocations can start. " + Math.max(burst - started, 0) + " are throttled. Those " + reserved + " reserved slots are also removed from the pool shared by functions with no reserved concurrency.";
      });
    }''',
        "best_title": "Classify the source, then cap the worker",
        "best": "Students first classify API Gateway, EventBridge, and SQS. They then set reserved concurrency to 20 against a burst of 80, and finally set it to 0. A pass includes the sentence: asynchronous Lambda retries twice, while an SQS failure is controlled by the queue's visibility timeout and maxReceiveCount.",
        "lab_title": "How does this invocation behave?",
        "lab_lede": "Choose the model or outcome. The calculator beside this lab is the second half of the exercise.",
        "will_not": [
            "Lambda will not run longer than 15 minutes.",
            "It will not keep a warm process for every future call unless you pay for provisioned concurrency.",
            "Attaching a function to a VPC does not give it a public IP or internet access.",
            "An SQS event source mapping is not an SNS-style push.",
            "A function cannot safely call itself through the same S3 prefix it writes. Filter prefixes or use two buckets.",
        ],
        "limits": [
            ["Timeout", "Maximum 900 seconds", "Do not use Lambda as a waiting API call for a long job."],
            ["Memory", "128 MB through 10,240 MB, with CPU growing as memory grows", "A CPU-bound function often gets faster when memory is raised."],
            ["Package", "50 MB zipped direct upload, 250 MB unzipped including layers, 10 GB container image", "Large dependencies belong in an image or layer, not a growing zip."],
            ["Account concurrency", "A regional pool, 1,000 by default", "One function can starve others unless reserved concurrency protects them."],
            ["Async retries", "Two retries, then destination or discard", "This is different from an SQS redrive policy."],
            ["Temporary disk", "/tmp can be raised up to 10 GB and disappears after the environment is reclaimed", "Durable output belongs in S3."],
        ],
        "cost_title": "Requests and GB-seconds, plus concurrency you keep warm",
        "cost_points": [
            "Standard Lambda bills per request and per GB-second of duration.",
            "Provisioned concurrency bills while the prepared environments exist, even with no traffic.",
            "A function in a VPC can add NAT or endpoint charges. Those are VPC charges, not a Lambda surcharge by themselves.",
            "Retries are extra invocations. A poison event that retries forever is a cost incident.",
        ],
        "cost_example": f"<strong class=\"text-white\">Example:</strong> one million 200 ms runs at 512 MB are a small Lambda bill. The expensive design is a function waiting 10 minutes on a remote system, or provisioned concurrency left at a high level overnight. {DOCS_NOTE}",
        "alt_title": "Use Lambda for short event work",
        "alternatives": [
            ["A request that must return quickly", "Lambda behind API Gateway", "Scale-to-zero and no instance patching."],
            ["A long container or always-on process", "Fargate or EC2", "Lambda's 15-minute limit and stateless disk are the wrong fit."],
            ["Many steps and human approval", "Step Functions calling Lambda", "The workflow, not one function, owns state and retries."],
            ["A steady high-throughput stream", "A tuned event source mapping, or a dedicated consumer", "Check batch size, concurrency, and shard behavior before adding more functions."],
            ["A job that needs a local GPU or persistent daemon", "EC2 or the matching managed service", "Lambda environments are temporary."],
        ],
        "waf": [
            ["Operational Excellence", "Structured logs include request id and business id.", "CloudWatch Logs"],
            ["Security", "One execution role per function and no static keys.", "Role policy"],
            ["Reliability", "Idempotent handlers, async destinations, and reserved concurrency for critical functions.", "Throttles and errors"],
            ["Performance Efficiency", "Memory sized to CPU need, batch size tuned, cold starts measured.", "Duration metric"],
            ["Cost Optimization", "Short duration, no idle provisioned concurrency, and no recursive trigger.", "Invocations"],
            ["Sustainability", "Avoid busy-wait retries. Let SQS or EventBridge carry the delay.", "Retry count"],
        ],
        "drills": [
            ["API Gateway REST calls Lambda, and the function is set to 15 minutes. The client still fails at 29 seconds. Why?", "The REST integration timeout is 29 seconds. The Lambda maximum does not extend the caller's wait."],
            ["Reserved concurrency for the report function is 0. A test invoke arrives. What happens?", "It is throttled. Zero means the function cannot run."],
            ["An SQS message fails inside Lambda. Where do you configure the move to a DLQ?", "On the SQS redrive policy with maxReceiveCount. Do not describe it as the asynchronous Lambda retry count."],
            ["A function in a private VPC subnet must read S3, and there is no NAT. What do you add?", "A gateway VPC endpoint for S3, plus a route and IAM permission."],
            ["S3 object-created invokes Lambda, and the function writes another object to the same prefix. What risk is that?", "A recursive loop. Use a different bucket or prefix, and a filter that excludes the output."],
        ],
        "docs": [
            ("Lambda Developer Guide", "https://docs.aws.amazon.com/lambda/latest/dg/welcome.html"),
            ("invocation", "https://docs.aws.amazon.com/lambda/latest/dg/lambda-invocation.html"),
            ("Lambda pricing", "https://aws.amazon.com/lambda/pricing/"),
        ],
        "cases": [
            {"prompt": "API Gateway receives a POST and waits for the function result.", "detail": "The client connection stays open.", "options": ["Synchronous", "Asynchronous, two retries", "SQS poller"], "answer": 0, "why": "A waiting API call is synchronous. The 29-second REST integration limit still applies."},
            {"prompt": "An EventBridge rule targets the function.", "detail": "The rule matched OrderPlaced.", "options": ["Synchronous", "Asynchronous", "Poll-based event source mapping"], "answer": 1, "why": "EventBridge invokes Lambda asynchronously. Lambda retries a failed async event twice."},
            {"prompt": "Messages sit on an SQS queue until the function reads them in batches.", "detail": "An event source mapping is configured.", "options": ["SNS push", "Asynchronous direct invoke", "Poll-based event source mapping"], "answer": 2, "why": "SQS uses a poller. Retries and the DLQ are queue settings."},
            {"prompt": "Reserved concurrency is 0. A new test invocation arrives.", "detail": "The account still has unused concurrency.", "options": ["It borrows account concurrency", "It is throttled"], "answer": 1, "why": "A reserved value of zero is an off switch for that function."},
            {"prompt": "The function is in a private subnet with only a local route. Its code calls the public S3 API.", "detail": "No NAT and no S3 endpoint.", "options": ["The call succeeds", "The call cannot reach S3"], "answer": 1, "why": "VPC attachment removes the default internet path. Add a gateway endpoint or NAT."},
        ],
    }


def eventbridge():
    return {
        "id": "eventbridge", "depth": 1, "path": "eventbridge/index.html",
        "title": "Amazon EventBridge Reference &amp; Live Labs",
        "description": "EventBridge rules, buses, archive and replay, comparisons with SNS and SQS, limits, and exam drills.",
        "accent": "text-fuchsia-400",
        "eyebrow": "Amazon EventBridge",
        "headline": "Route the event by its content, then let a queue do the waiting",
        "lede": "EventBridge is a serverless event bus. A producer puts an event once. Rules match the event and send it to targets. It is the right tool when the path depends on what the event says, when a SaaS application is the source, or when you need archive and replay.",
        "diagram": [("lambda", "Publisher", "PutEvents"), ("events", "Bus", "rules match"), ("sqs", "Target", "queue or API")],
        "jumps": bp.JUMPS,
        "summary_title": "A rule is a route, not a backlog",
        "summary": "The default bus receives many AWS service events. A custom bus isolates an application such as Northline or Clearfile. Partner buses receive supported SaaS events. A rule can have more than one target, but a consumer that can be down for an hour should be an SQS target. Archive and replay answer a question SNS and SQS do not answer by themselves: show me those events again.",
        "bad_title": "Every consumer is a Lambda target with no buffer",
        "bad": [
            "A slow billing function is invoked directly and drops work when it throttles.",
            "Email is expected from the bus even though the bus has no email subscriber.",
            "A bad deploy cannot be repaired by replaying yesterday because nothing was archived.",
        ],
        "good_title": "Rules select the work. SQS owns the wait.",
        "good": [
            "High-value orders match a numeric filter and land on a fraud queue.",
            "Every order matches a second rule whose target is SNS or SQS.",
            "The custom bus can be archived. Replay is a controlled operation, not an automatic retry.",
        ],
        "compare_title": "EventBridge, SNS, and SQS can appear in the same correct answer",
        "compare_headers": ["Question the exam asks", "Choose", "Reason"],
        "compare_rows": [
            ["Route by JSON content, SaaS source, or cross-account bus", "EventBridge", "Rules, archive, replay, schema registry, and pipes are the clues."],
            ["Push one message to email, SMS, mobile, and several queues", "SNS", "Native subscriber protocols and high-volume fan-out."],
            ["Keep work until one worker pool finishes it", "SQS", "Visibility timeout, long polling, and a redrive policy."],
            ["Send a scheduled one-time job", "EventBridge Scheduler", "A schedule is not the same object as a content rule."],
            ["Poll SQS and call an API with a filter and enrichment step", "EventBridge Pipes", "The pipe owns the poll. A normal rule does not poll a queue."],
            ["Remember the event for a week and try a fixed consumer again", "Archive and replay, usually with SQS in front of the consumer", "Replay is not an SQS DLQ redrive."],
        ],
        "extra": '''<section class="mt-12 rounded-2xl border border-slate-800 bg-slate-900 p-6 sm:p-8">
          <p class="text-[11px] font-medium uppercase tracking-[0.18em] text-fuchsia-400">Rule used in the lab</p>
          <h2 class="mt-2 text-2xl font-semibold text-white">Fraud matches amount, not the name of the queue</h2>
          <pre class="mt-4 overflow-x-auto rounded-xl bg-black p-4 text-xs leading-6 text-fuchsia-200">{
  "source": ["northline.orders"],
  "detail-type": ["OrderPlaced"],
  "detail": { "amount": [{ "numeric": [">=", 1000] }] }
}</pre>
          <p class="mt-4 text-sm leading-6 text-slate-400">A second rule matches every OrderPlaced event and targets the fan-out topic. Multiple rules can match the same event. A rule does not stop later rules.</p>
        </section>''',
        "best_title": "Match the rule, then name the service that should wait",
        "best": "Students decide whether the fraud rule matches, which service sends email, and where a crashed worker's backlog lives. The passing explanation is: EventBridge selects the target, SNS reaches an email subscriber, and SQS holds the work. Archive and replay is the recovery tool for the bus, not a replacement for a DLQ.",
        "lab_title": "What happens to this event?",
        "lab_lede": "Use the fraud rule above. Decide whether it matches, and which service owns the next responsibility.",
        "will_not": [
            "EventBridge does not store a consumer backlog. Target a queue for that.",
            "It does not provide SQS visibility timeout or maxReceiveCount.",
            "A standard rule does not poll Kinesis or SQS. Pipes is the polling feature.",
            "It does not send SMS or email by itself. Target SNS when a person must be notified.",
            "Matching is at least once. Consumers still need to be idempotent.",
        ],
        "limits": [
            ["Event size", "256 KB", "Put a large document in S3 and send the key in the event."],
            ["PutEvents", "Up to 10 events in one call", "Batch the publish when the producer has a burst."],
            ["Delivery", "At least once, and target retries can continue for up to 24 hours", "This retry is not the same as two Lambda async retries or an SQS receive count."],
            ["DLQ", "A target can use an SQS DLQ after delivery retries are exhausted", "The DLQ catches delivery failure, not a bug after the consumer accepted the message."],
            ["Buses", "Default, custom, and partner buses isolate sources", "Do not put two products on one custom bus just because it is convenient."],
            ["Order", "No global order guarantee", "Use FIFO SNS or FIFO SQS only where order is a real requirement."],
        ],
        "cost_title": "Custom events are the bill. AWS service events often are not.",
        "cost_points": [
            "Many events published by AWS services to the default bus have no EventBridge event charge. Confirm the current pricing page.",
            "Custom events, such as Northline OrderPlaced, are billed per million.",
            "Archive storage, replay, schema discovery, and cross-Region delivery can add charges.",
            "The SQS, SNS, and Lambda targets bill separately.",
        ],
        "cost_example": f"<strong class=\"text-white\">Example:</strong> ten million custom order events are ten million EventBridge events before any target runs. Routing them to three SQS queues does not multiply the EventBridge publish into three publishes, but it does create three queue deliveries. {DOCS_NOTE}",
        "alt_title": "Start from the behavior, not the newest service",
        "alternatives": [
            ["Content routing, SaaS, archive, and replay", "EventBridge", "The event itself chooses the route."],
            ["Email, SMS, mobile push, and simple fan-out", "SNS", "Subscriber protocols are the clue."],
            ["Durable work for one team", "SQS", "The consumer polls when it is ready."],
            ["Ordered retained stream and multiple readers", "Kinesis", "Readers move through a retained log."],
            ["A clock, including a one-time clock", "EventBridge Scheduler", "Do not approximate a one-time job with a queue delay unless the delay fits SQS."],
        ],
        "waf": [
            ["Operational Excellence", "Rules and example events are versioned with the application.", "Contract tests"],
            ["Security", "A resource policy controls who can put events. Targets use their own roles.", "Bus policy"],
            ["Reliability", "SQS targets, DLQs, archive, and idempotent consumers.", "Failed invocations"],
            ["Performance Efficiency", "Filters drop useless events before a costly target.", "Matched event count"],
            ["Cost Optimization", "Keep payloads small and avoid a rule that invokes an expensive function for every heartbeat.", "Custom events"],
            ["Sustainability", "Do not replay an archive on a schedule. Replay a bounded window after a real defect.", "Replay count"],
        ],
        "drills": [
            ["An event must reach email and a durable worker. Which combination fits?", "EventBridge or the application publishes to SNS, and SNS has an email subscription and an SQS subscription. EventBridge can also target both SNS and SQS."],
            ["A worker was deployed with a bug yesterday. The events were archived. How do you try them again?", "Replay the archive for that time window into the bus or a recovery target. Then fix the consumer so the replay is idempotent."],
            ["The fraud rule requires amount >= 1000. An order for 999 arrives. Does the fraud target run?", "No. Other rules, such as the all-orders rule, can still match."],
            ["A team uses EventBridge to poll an SQS queue and enrich the message before calling an API. Which feature is that?", "EventBridge Pipes, not a normal bus rule."],
            ["Two rules match one event. Does the first matching rule stop the second?", "No. All matching rules run."],
        ],
        "docs": [
            ("EventBridge User Guide", "https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-what-is.html"),
            ("event patterns", "https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-event-patterns.html"),
            ("EventBridge pricing", "https://aws.amazon.com/eventbridge/pricing/"),
        ],
        "cases": [
            {"prompt": "OrderPlaced arrives with amount 1500. The fraud rule matches amount >= 1000.", "detail": "source northline.orders; detail-type OrderPlaced.", "options": ["Fraud target runs", "Fraud target does not run"], "answer": 0, "why": "1500 satisfies the numeric filter. The all-orders rule can also match at the same time."},
            {"prompt": "The same event arrives with amount 40.", "detail": "The fraud rule is unchanged.", "options": ["Fraud target runs", "Fraud target does not run"], "answer": 1, "why": "40 fails the numeric filter. A broader OrderPlaced rule can still route it."},
            {"prompt": "A matched event must also reach an email address. Which service owns email delivery?", "detail": "The bus has no email subscriber.", "options": ["EventBridge email target", "SNS", "SQS"], "answer": 1, "why": "Target SNS for email, SMS, or mobile push. SQS is the durable worker path."},
            {"prompt": "The billing worker is down for two hours. Where should the orders wait?", "detail": "You can choose the rule target.", "options": ["Inside the EventBridge rule", "On an SQS target", "In a Lambda /tmp directory"], "answer": 1, "why": "SQS is the backlog. EventBridge routing does not replace a queue."},
            {"prompt": "Yesterday's events were wrongfully processed and the bus has an archive. What recovers them?", "detail": "The consumer has been fixed and made idempotent.", "options": ["SQS redrive", "Archive and replay", "A NAT gateway"], "answer": 1, "why": "Replay reads the archive. An SQS redrive only works for messages that are still on a DLQ."},
        ],
    }
