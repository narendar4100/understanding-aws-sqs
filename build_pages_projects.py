from pathlib import Path

import build_pages as bp
import build_pages_content as content

ROOT = Path(__file__).resolve().parent / "frontend"


def northline():
    return {
        "id": "northline", "depth": 2, "path": "projects/northline/index.html",
        "title": "Northline — Secure Order Pipeline",
        "description": "Northline is the secure order pipeline lab across IAM, VPC, S3, Lambda, EventBridge, SNS, and SQS.",
        "accent": "text-cyan-400",
        "eyebrow": "Project Northline · Secure Order Pipeline",
        "headline": "Accept the order once, then let every team consume its own copy",
        "lede": "Northline is a checkout flow. The API returns as soon as the receipt is stored and the event is published. Fraud, billing, and shipping never share a role, a queue, or a failure domain.",
        "diagram": [("users", "Customer", "one order"), ("apigw", "API", "waits briefly"), ("s3", "Receipt", "private object"), ("events", "Route", "by amount"), ("sqs", "Queues", "own the wait")],
        "jumps": bp.JUMPS,
        "summary_title": "One business event, seven services, three independent consumers",
        "summary": "The accept function writes orders/&lt;orderId&gt;.json to a private S3 bucket and publishes OrderPlaced to the Northline event bus. A fraud rule matches amounts of 1000 or more and targets the fraud queue directly. A second rule matches every order and targets an SNS topic. Billing subscribes with no filter. Shipping subscribes with an itemType filter of physical. Each subscription has its own SQS queue and DLQ.",
        "bad_title": "The API charges the card and emails the warehouse",
        "bad": [
            "The customer waits while fraud, payment, and shipping all finish.",
            "A shipping outage returns HTTP 500 and the receipt was never stored.",
            "One admin role lets every function read and delete every bucket.",
        ],
        "good_title": "Accept, store, publish, then fan out through buffers",
        "good": [
            "The API function has permission to write one prefix and put one event.",
            "EventBridge selects the route. SNS fans out. SQS lets a team go offline.",
            "Workers in the production design use private subnets and an S3 gateway endpoint, with no NAT gateway required for S3.",
        ],
        "compare_title": "Who is allowed to touch each resource",
        "compare_headers": ["Role", "May do", "Must not do"],
        "compare_rows": [
            ["northline-accept", "PutObject on incoming receipts; PutEvents on the Northline bus", "Read the fraud queue or delete an object"],
            ["northline-billing", "Receive and delete its own queue; GetObject on receipts", "Publish a new order or consume the shipping queue"],
            ["northline-shipping", "Receive and delete its own queue; GetObject on receipts", "See digital-only orders after the filter is in place"],
            ["northline-fraud", "Receive and delete the fraud queue; GetObject on high-value receipts", "Change the EventBridge rule"],
            ["EventBridge target role", "Send to the fraud queue and publish to the topic", "Use a wildcard on every queue in the account"],
            ["Student operator", "Describe resources and read logs in the lab account", "Attach AdministratorAccess to a function"],
        ],
        "extra": '''<section class="mt-12 rounded-2xl border border-slate-800 bg-slate-900 p-6 sm:p-8">
          <p class="text-[11px] font-medium uppercase tracking-[0.18em] text-cyan-400">Service map</p>
          <h2 class="mt-2 text-2xl font-semibold text-white">Every service has one job</h2>
          <div class="mt-6 overflow-x-auto rounded-xl border border-slate-800"><table class="w-full min-w-[760px] text-left text-sm"><thead class="bg-slate-950 text-slate-300"><tr><th class="px-4 py-3">Service</th><th class="px-4 py-3">Northline job</th><th class="px-4 py-3">Exam point</th></tr></thead><tbody class="divide-y divide-slate-800 text-slate-400">
            <tr><td class="px-4 py-3 text-white">IAM</td><td class="px-4 py-3">One role per function and a trust policy for Lambda.</td><td class="px-4 py-3">A shared access key is the wrong answer.</td></tr>
            <tr><td class="px-4 py-3 text-white">VPC</td><td class="px-4 py-3">Private worker subnets in two AZs and a gateway endpoint for S3.</td><td class="px-4 py-3">Do not add a NAT gateway only to reach S3.</td></tr>
            <tr><td class="px-4 py-3 text-white">S3</td><td class="px-4 py-3">Versioned, encrypted, Block Public Access receipts.</td><td class="px-4 py-3">The event carries the key, not the whole document.</td></tr>
            <tr><td class="px-4 py-3 text-white">Lambda</td><td class="px-4 py-3">Short accept function and separate consumers.</td><td class="px-4 py-3">API Gateway still times out at 29 seconds.</td></tr>
            <tr><td class="px-4 py-3 text-white">EventBridge</td><td class="px-4 py-3">Custom bus, fraud rule, all-orders rule, archive.</td><td class="px-4 py-3">Both rules can match one event.</td></tr>
            <tr><td class="px-4 py-3 text-white">SNS</td><td class="px-4 py-3">OrderPlaced topic with billing and shipping subscriptions.</td><td class="px-4 py-3">The shipping filter does not affect the fraud queue.</td></tr>
            <tr><td class="px-4 py-3 text-white">SQS</td><td class="px-4 py-3">Billing, shipping, and fraud queues, each with a DLQ.</td><td class="px-4 py-3">A consumer bug uses the queue redrive policy.</td></tr>
          </tbody></table></div>
        </section>''',
        "best_title": "Place four orders and name every queue that receives one",
        "best": "Run the live lab from memory first. Digital $40 reaches billing only. Physical $80 reaches billing and shipping. Digital $2000 reaches fraud and billing. Physical $1500 reaches fraud, billing, and shipping. A student who adds shipping to the digital order, or who sends fraud through the SNS filter, repeats the case. Finish by writing the IAM action each role needs and by saying why the class design does not create a NAT gateway.",
        "lab_title": "Which queues receive this Northline order?",
        "lab_lede": "Fraud is an EventBridge target, not an SNS subscriber. Shipping is an SNS subscription filtered to physical items. Billing receives every order that reaches the topic.",
        "will_not": [
            "Northline does not make payment exactly once. The billing consumer must record the order id before it charges.",
            "It does not roll back shipping because billing failed. The teams compensate; they do not share one transaction.",
            "The event bus does not retain a backlog. The queues do.",
            "A filter is not authorization. Shipping must still reject an unexpected message.",
            "The production VPC design is not a public subnet with a wide-open security group.",
        ],
        "limits": [
            ["Accept path", "Return after S3 and PutEvents succeed", "Do not wait for shipping inside the API call."],
            ["Event size", "Send the receipt key, not a 5 MB invoice", "EventBridge events are limited to 256 KB."],
            ["Fraud rule", "amount >= 1000", "999 does not match, and a second rule may still match."],
            ["Shipping filter", "itemType physical", "Digital orders are not a failed delivery. They are filtered out."],
            ["Queue failure", "maxReceiveCount on that queue", "An SNS DLQ would be for a delivery failure, not a bad invoice."],
            ["Network", "S3 gateway endpoint, interface endpoints only where privacy requires them", "A week-long NAT gateway is the wrong student default."],
        ],
        "cost_title": "The multiplier is consumers, not the number of services on the diagram",
        "cost_points": [
            "One custom EventBridge event plus one S3 PUT is the accept cost.",
            "SNS to SQS has no SNS per-message delivery charge, and each queue still bills its own requests.",
            "Three queues mean three consumers, three sets of logs, and three possible DLQs.",
            "A NAT gateway left running will dominate this bill. The lab does not need one.",
        ],
        "cost_example": "<strong class=\"text-white\">Example:</strong> 10 million orders with the all-orders rule and two SNS subscriptions create 10 million custom events and 20 million SQS deliveries, plus extra fraud deliveries for the high-value subset. Price the current EventBridge, SNS, SQS, S3, and Lambda pages before you quote a total.",
        "alt_title": "Change Northline only when the requirement changes",
        "alternatives": [
            ["A person must approve a high-value order", "Step Functions with a task token", "EventBridge can start it, but the approval state is a workflow."],
            ["Shipping must stay strictly ordered per customer", "FIFO SQS with a message group per customer", "Standard queues are the wrong promise."],
            ["A partner SaaS must emit the order", "EventBridge partner event source", "Do not scrape the partner from a Lambda loop."],
            ["The receipt must be queried with SQL", "Athena on the bucket, or a table written by billing", "S3 remains the object store."],
        ],
        "waf": [
            ["Operational Excellence", "Order id flows through S3, the event, and every log line.", "Correlation id"],
            ["Security", "Separate roles, private bucket, encrypted objects, and no public queue policy.", "Access Analyzer"],
            ["Reliability", "Queues, DLQs, archive, and idempotent billing.", "DLQ alarm"],
            ["Performance Efficiency", "The API stops at publish. Consumers scale on queue depth.", "Accept latency"],
            ["Cost Optimization", "Gateway endpoint for S3 and no idle NAT.", "NAT hours at zero"],
            ["Sustainability", "Filters remove digital orders from the shipping consumer.", "Empty receives"],
        ],
        "drills": [
            ["Digital order, amount 40. Which queues receive it?", "Billing only. Fraud does not match. Shipping is filtered out."],
            ["The shipping function crashes after it has deleted the message. What protects the customer?", "Nothing in SQS can bring that deleted message back. The consumer must delete only after the work is durable, and the business event must be idempotent on replay."],
            ["Why is the fraud queue not another SNS subscription?", "It is a direct EventBridge target so a fraud outage is isolated from the topic. Either design can work; the exam point is to say which resource owns the retry."],
            ["Workers are moved into a private subnet and can no longer read receipts. What is the smallest network fix?", "An S3 gateway endpoint and the prefix-list route. Do not start with a NAT gateway."],
            ["Billing reports a duplicate charge after a timeout. Where is the defect?", "The consumer applied the side effect before recording the order id. The queue delivered at least once, which is its contract."],
        ],
        "docs": [
            ("EventBridge patterns", "https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-event-patterns.html"),
            ("SNS filter policies", "https://docs.aws.amazon.com/sns/latest/dg/sns-message-filtering.html"),
            ("SQS dead-letter queues", "https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html"),
        ],
        "cases": [
            {"prompt": "Digital order for $40.", "detail": "itemType digital. amount 40. Fraud rule is amount >= 1000. Shipping filter is physical.", "options": ["Billing only", "Billing and shipping", "Fraud and billing", "Fraud, billing, and shipping"], "answer": 0, "why": "The all-orders rule reaches SNS. Billing has no filter. Shipping rejects the item type. Fraud does not match."},
            {"prompt": "Physical order for $80.", "detail": "itemType physical. amount 80.", "options": ["Billing only", "Billing and shipping", "Fraud and billing", "Fraud, billing, and shipping"], "answer": 1, "why": "Billing and shipping both receive it. 80 is below the fraud rule."},
            {"prompt": "Digital order for $2000.", "detail": "itemType digital. amount 2000.", "options": ["Billing only", "Billing and shipping", "Fraud and billing", "Fraud, billing, and shipping"], "answer": 2, "why": "EventBridge sends it to the fraud queue and to SNS. Shipping is filtered out because the item is digital."},
            {"prompt": "Physical order for $1500.", "detail": "itemType physical. amount 1500.", "options": ["Billing only", "Billing and shipping", "Fraud and billing", "Fraud, billing, and shipping"], "answer": 3, "why": "Fraud matches the amount, and both SNS subscriptions match."},
            {"prompt": "The shipping consumer throws for a valid physical order until maxReceiveCount is reached. Where does that message wait for repair?", "detail": "SNS already delivered the message to the shipping queue.", "options": ["EventBridge archive automatically", "The shipping queue DLQ", "The billing queue"], "answer": 1, "why": "This is a processing failure on one queue. Billing is unaffected. Archive and replay is a separate bus feature, not the DLQ."},
        ],
    }


def clearfile():
    return {
        "id": "clearfile", "depth": 2, "path": "projects/clearfile/index.html",
        "title": "Clearfile — Document Processing Pipeline",
        "description": "Clearfile is the document pipeline lab across S3, IAM, EventBridge, SQS, Lambda, SNS, and VPC.",
        "accent": "text-indigo-400",
        "eyebrow": "Project Clearfile · Document Processing Pipeline",
        "headline": "Upload the file directly, then route it by what it is",
        "lede": "Clearfile accepts documents without sending the bytes through Lambda. The browser uploads to a private prefix with a presigned URL. EventBridge routes the created object. Queues absorb extract and image work, and SNS tells the downstream teams when a result is ready.",
        "diagram": [("users", "Browser", "presigned PUT"), ("s3", "Incoming", "object key"), ("events", "Rules", "by suffix"), ("sqs", "Work", "retry there"), ("lambda", "Result", "processed/")],
        "jumps": bp.JUMPS,
        "summary_title": "The bucket is the front door. The bus is the router.",
        "summary": "The uploader role can create a presigned PUT for incoming/* and nothing else. S3 sends the object-created event to the Clearfile bus. A .pdf rule targets the extract queue. Image suffixes target the image queue. Any other suffix stays in incoming/ until a person or a lifecycle rule handles it. Workers write results to processed/ and publish DocumentReady. They cannot delete the original while Object Lock governance is active.",
        "bad_title": "The API receives every byte and writes every result with admin rights",
        "bad": [
            "A 2 GB scan is posted through API Gateway and Lambda.",
            "The same function creates thumbnails, extracts text, and emails the user.",
            "A failed PDF is retried in memory until the invocation times out.",
        ],
        "good_title": "Direct upload, typed routes, and a queue per job",
        "good": [
            "The browser uploads to S3. Lambda sees the key, not the whole transfer.",
            "EventBridge suffix rules separate PDF and image work.",
            "A poison PDF reaches the extract DLQ without stopping the image queue.",
        ],
        "compare_title": "Separate the person uploading from the code processing",
        "compare_headers": ["Principal", "Permission", "Why it is narrow"],
        "compare_rows": [
            ["Uploader role", "s3:PutObject on incoming/*", "A leaked browser session cannot list or delete the archive."],
            ["Extract role", "Get incoming object, Put processed result, receive extract queue, publish DocumentReady", "It cannot change the bucket policy or consume the image queue."],
            ["Image role", "The image queue and the processed prefix only", "A thumbnail bug cannot discard PDFs."],
            ["Notification role", "Receive the notify queue", "It does not need s3:DeleteObject."],
            ["Bucket", "Block Public Access, versioning, SSE-KMS, Object Lock governance", "Public read is not a substitute for a presigned URL."],
            ["VPC path", "Workers in private subnets use an S3 gateway endpoint", "The upload from the browser uses S3's public HTTPS endpoint with a signature. That is a different path from the worker path."],
        ],
        "extra": '''<section class="mt-12 rounded-2xl border border-slate-800 bg-slate-900 p-6 sm:p-8">
          <p class="text-[11px] font-medium uppercase tracking-[0.18em] text-indigo-400">Service map</p>
          <h2 class="mt-2 text-2xl font-semibold text-white">The file moves only when a worker writes a new object</h2>
          <div class="mt-6 overflow-x-auto rounded-xl border border-slate-800"><table class="w-full min-w-[760px] text-left text-sm"><thead class="bg-slate-950 text-slate-300"><tr><th class="px-4 py-3">Service</th><th class="px-4 py-3">Clearfile job</th><th class="px-4 py-3">Exam point</th></tr></thead><tbody class="divide-y divide-slate-800 text-slate-400">
            <tr><td class="px-4 py-3 text-white">S3</td><td class="px-4 py-3">Incoming and processed prefixes, versioning, encryption, Object Lock.</td><td class="px-4 py-3">A prefix is not a security boundary unless the IAM policy uses that ARN.</td></tr>
            <tr><td class="px-4 py-3 text-white">IAM</td><td class="px-4 py-3">Presign with the uploader role. Workers have their own roles.</td><td class="px-4 py-3">A presigned URL expires and cannot exceed the role.</td></tr>
            <tr><td class="px-4 py-3 text-white">EventBridge</td><td class="px-4 py-3">Object Created rules for PDF and image suffixes.</td><td class="px-4 py-3">An unmatched object is not an error event.</td></tr>
            <tr><td class="px-4 py-3 text-white">SQS</td><td class="px-4 py-3">Extract queue, image queue, and a DLQ for each.</td><td class="px-4 py-3">Processing failure is a receive count, not an S3 error.</td></tr>
            <tr><td class="px-4 py-3 text-white">Lambda</td><td class="px-4 py-3">Extract text or build a thumbnail, then publish the result.</td><td class="px-4 py-3">Do not upload the original through the function.</td></tr>
            <tr><td class="px-4 py-3 text-white">SNS</td><td class="px-4 py-3">DocumentReady to the indexer and the notifier.</td><td class="px-4 py-3">Fan-out happens after success, not at upload.</td></tr>
            <tr><td class="px-4 py-3 text-white">VPC</td><td class="px-4 py-3">Private workers reach S3 through a gateway endpoint.</td><td class="px-4 py-3">The browser upload does not travel through the NAT gateway.</td></tr>
          </tbody></table></div>
        </section>''',
        "best_title": "Route four files, including the file you do not process",
        "best": "Students predict the path for contract.pdf, photo.jpg, notes.txt, and a PDF that always throws. The text file must remain in incoming/. The broken PDF must end on the extract DLQ, while photo work continues. The written answer names the presigned URL permission, the suffix rule, the queue DLQ, and the Object Lock behavior that stops the worker from deleting the original.",
        "lab_title": "Where does this file go?",
        "lab_lede": "PDF rules and image rules are independent. An unknown suffix has no target. A worker exception happens after the message is already on a queue.",
        "will_not": [
            "Clearfile does not scan for malware unless you add that worker. Do not claim the pipeline is safe because it uses SQS.",
            "EventBridge does not move, copy, or delete the object.",
            "A presigned URL placed in a log is a bearer token until it expires.",
            "Object Lock governance is not Compliance mode. A privileged principal can still override governance. Compliance mode is the choice when nobody may shorten retention.",
            "The image queue does not inherit the extract queue's DLQ.",
        ],
        "limits": [
            ["Upload size", "Use S3 multipart for large scans. Do not post the file to API Gateway.", "The API payload limit is the wrong front door."],
            ["Presigned URL", "Short expiry, one key, PutObject only", "A week-long URL is a leaked credential."],
            ["Unmatched suffix", "No rule means no queue message", "Add a lifecycle or an explicit reject rule if unknowns must be quarantined."],
            ["Poison file", "Extract DLQ after maxReceiveCount", "The image worker keeps running."],
            ["Result event", "Publish DocumentReady only after the result PUT succeeds", "SNS is the success fan-out, not the retry mechanism."],
            ["Retention", "Governance can be overridden; compliance cannot", "Say which mode the bucket uses. This lab uses governance."],
        ],
        "cost_title": "Large objects cost storage and requests, not EventBridge payload",
        "cost_points": [
            "The document bytes are billed as S3 storage and PUT requests, not as a giant EventBridge event.",
            "Each matched object creates one custom event and one SQS send.",
            "A retry reads the object again. A poison file multiplies GET requests until the DLQ.",
            "KMS encryption adds key requests. That is often the surprise line on a document workload.",
        ],
        "cost_example": "<strong class=\"text-white\">Example:</strong> one million 2 MB PDFs are an S3 storage and request cost. The EventBridge events stay small because they contain the bucket and key. Reprocessing all of them through a bug is the cost incident, which is why the DLQ must stop the loop.",
        "alt_title": "Keep Clearfile when the work is an object pipeline",
        "alternatives": [
            ["A user-facing synchronous thumbnail", "A small Lambda only if the file is already small and the user is waiting", "Large files still upload to S3 first."],
            ["Full-text search", "A consumer on DocumentReady writes the index", "S3 is not the search engine."],
            ["Records that can never be deleted early", "Object Lock compliance mode", "Stronger than the governance mode used in this lab."],
            ["A shared filesystem between editors", "EFS or FSx", "Clearfile is an object pipeline, not a home directory."],
        ],
        "waf": [
            ["Operational Excellence", "Suffix rules and sample keys are test cases.", "Four-file lab"],
            ["Security", "Private bucket, short presign, separate roles, encryption, access logs.", "Block Public Access"],
            ["Reliability", "Independent queues and DLQs. Versioning protects against a bad overwrite.", "DLQ depth"],
            ["Performance Efficiency", "Direct-to-S3 upload and suffix filters.", "API payload size"],
            ["Cost Optimization", "Lifecycle for incoming leftovers and Intelligent-Tiering for old results.", "Incomplete multipart cleanup"],
            ["Sustainability", "Do not reprocess every historical object after a small code change. Replay a bounded set.", "DLQ redrive count"],
        ],
        "drills": [
            ["A 2 GB scan must enter the system. Which upload path passes the exam?", "Presigned multipart upload to S3. Not API Gateway and not a Lambda request body."],
            ["notes.txt is uploaded. What runs?", "Nothing. No rule matches, and the object remains in incoming/."],
            ["The extract function deletes the source PDF and the bucket uses Object Lock governance. What can stop it?", "The lock, if the retention is active and the role lacks the permission to override governance. IAM should also omit s3:DeleteObject."],
            ["Photo processing is healthy, and one PDF fails forever. What isolates the failure?", "The PDF has its own queue and DLQ. It does not share the image queue."],
            ["DocumentReady is published before the result PUT. The indexer runs. What is wrong?", "The message claims a result that is not durable. Publish only after the PUT succeeds, and make the indexer tolerate a retry."],
        ],
        "docs": [
            ("S3 presigned URLs", "https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html"),
            ("S3 Object Lock", "https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html"),
            ("EventBridge and S3", "https://docs.aws.amazon.com/AmazonS3/latest/userguide/EventBridge.html"),
        ],
        "cases": [
            {"prompt": "The browser uploads incoming/contract.pdf.", "detail": "Object Created. A rule matches suffix .pdf and targets the extract queue.", "options": ["Extract queue", "Image queue", "No rule; it stays in incoming/", "Extract DLQ immediately"], "answer": 0, "why": "The suffix rule sends one message to the extract queue. The DLQ is not involved yet."},
            {"prompt": "The browser uploads incoming/photo.jpg.", "detail": "A second rule matches .jpg, .jpeg, and .png.", "options": ["Extract queue", "Image queue", "Both work queues", "No rule; it stays in incoming/"], "answer": 1, "why": "Only the image rule matches. Rules do not fall through into each other."},
            {"prompt": "The browser uploads incoming/notes.txt.", "detail": "No rule uses the .txt suffix.", "options": ["Extract queue", "Image queue", "No rule; it stays in incoming/", "SNS DocumentReady"], "answer": 2, "why": "Unmatched is not a failed delivery. Nothing is published, and the object remains where it was uploaded."},
            {"prompt": "contract.pdf matches and the extractor throws until maxReceiveCount.", "detail": "The image queue has its own messages and is healthy.", "options": ["Extract DLQ", "Image DLQ", "EventBridge drops the upload", "S3 deletes the PDF"], "answer": 0, "why": "The processing failure belongs to the extract queue's redrive policy. S3 still has the object."},
            {"prompt": "A worker tries to delete the original before governance retention ends, and its role has no lock-override permission.", "detail": "Object Lock governance is active.", "options": ["The delete succeeds", "The delete is denied"], "answer": 1, "why": "Governance plus a role that cannot override it protects the original. Compliance mode would protect it even from a principal that has the override permission."],
        ],
    }


def write_home():
    lab_cases = [
        {"prompt": "One team must buffer orders and retry them with its own DLQ.", "detail": "A second team must not consume the same message.", "options": ["SQS", "SNS", "EventBridge", "S3"], "answer": 0, "why": "SQS is the point-to-point buffer. Fan-out requires a copy per consumer."},
        {"prompt": "One paid event must reach email and two independent workers.", "detail": "The workers can be offline.", "options": ["SNS to email and two SQS queues", "One SQS queue polled by all three", "A public S3 bucket"], "answer": 0, "why": "SNS provides the email protocol and a separate queue subscription for each worker."},
        {"prompt": "Orders must be routed by amount, archived, and replayed after a bad deploy.", "detail": "The producer should publish once.", "options": ["EventBridge", "SQS FIFO only", "IAM"], "answer": 0, "why": "Content rules plus archive and replay are EventBridge. Put SQS behind the consumer."},
        {"prompt": "A private instance must read S3, and the design forbids a NAT gateway.", "detail": "The instance has no public IP.", "options": ["Gateway VPC endpoint", "A second internet gateway", "SNS"], "answer": 0, "why": "S3 and DynamoDB gateway endpoints stay on the AWS network and have no NAT hourly charge."},
        {"prompt": "A 2 GB statement must be stored privately and read back by its key.", "detail": "It is an object, not a row that needs SQL.", "options": ["S3", "A Lambda /tmp file", "SQS message body"], "answer": 0, "why": "S3 holds the object. SQS and EventBridge have much smaller payload limits."},
        {"prompt": "Each API request needs about 200 ms of validation and must scale to zero.", "detail": "No server to patch.", "options": ["Lambda", "A NAT gateway", "S3 Standard-IA"], "answer": 0, "why": "Lambda fits a short stateless validation. The API integration still has its own timeout."},
        {"prompt": "A worker function must never use more than 10 concurrent executions.", "detail": "The account pool has unused concurrency.", "options": ["Reserved concurrency of 10", "A larger memory setting", "A public subnet"], "answer": 0, "why": "Reserved concurrency is the cap. It also removes those 10 slots from the shared pool."},
        {"prompt": "A partner account needs temporary access to one bucket.", "detail": "The partner already has an AWS account.", "options": ["Cross-account role and bucket policy", "The root access key by email", "A public bucket policy"], "answer": 0, "why": "Both sides allow the role, and the credentials are temporary. A public bucket or a root key fails the security decision."},
    ]
    cards = [
        ("iam/", "IAM", "amber", "Evaluation order, roles, SCPs, and permission boundaries."),
        ("vpc/", "VPC", "sky", "Routes, security groups, NACLs, NAT, and endpoints."),
        ("s3/", "S3", "green", "Storage classes, consistency, public access, and Object Lock."),
        ("lambda/", "Lambda", "orange", "Sync, async, pollers, concurrency, and VPC access."),
        ("sqs/", "SQS", "emerald", "The existing live AWS queue lab: Standard, FIFO, and DLQs."),
        ("sns/", "SNS", "violet", "Fan-out, filter policies, delivery retries, and subscriber DLQs."),
        ("eventbridge/", "EventBridge", "fuchsia", "Rules, archive and replay, Scheduler, and Pipes."),
    ]
    card_html = []
    for href, title, color, text in cards:
        card_html.append(f'''<a href="{href}" class="rounded-2xl border border-slate-800 bg-slate-900 p-6 transition hover:-translate-y-1 hover:border-{color}-500">
          <p class="text-xs font-medium uppercase tracking-wider text-{color}-300">{title}</p>
          <p class="mt-3 text-sm leading-6 text-slate-400">{text}</p>
        </a>''')
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="description" content="AWS architecture labs for IAM, VPC, S3, Lambda, SQS, SNS, and EventBridge, plus the Northline and Clearfile projects." />
  <title>AWS Architecture Lab</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&amp;family=IBM+Plex+Sans:wght@400;500;600&amp;display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="assets/site.css" />
  <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
</head>
<body class="min-h-screen bg-slate-950 text-slate-100 antialiased">
  <header class="border-b border-slate-800">
    {bp.nav("", "home")}
  </header>
  <main class="mx-auto max-w-6xl px-6 py-14">
    <p class="text-xs font-medium uppercase tracking-[0.2em] text-emerald-400">Service pages and two capstone systems</p>
    <h1 class="mt-4 max-w-4xl text-4xl font-semibold tracking-tight text-white sm:text-6xl">Learn the decision AWS exams actually test.</h1>
    <p class="mt-6 max-w-3xl text-lg leading-8 text-slate-400">Each page has an architecture, a fragile design beside a sound one, a live decision lab, limits, cost, alternatives, and original exam drills. SQS still calls the deployed API. The new labs train the same decisions without creating NAT gateways or public buckets.</p>
    <ol class="mt-8 grid gap-3 text-sm leading-6 text-slate-300 md:grid-cols-3">
      <li class="rounded-xl border border-slate-800 bg-slate-900 p-4"><span class="font-mono text-xs text-emerald-300">01</span><p class="mt-2">IAM and VPC. Learn who can call, and which network path exists.</p></li>
      <li class="rounded-xl border border-slate-800 bg-slate-900 p-4"><span class="font-mono text-xs text-emerald-300">02</span><p class="mt-2">S3 and Lambda. Store the object, then decide how the code is invoked.</p></li>
      <li class="rounded-xl border border-slate-800 bg-slate-900 p-4"><span class="font-mono text-xs text-emerald-300">03</span><p class="mt-2">SQS, SNS, and EventBridge. Buffer, fan out, or route. Then build Northline and Clearfile.</p></li>
    </ol>
    <div class="mt-10 grid gap-4 md:grid-cols-2 xl:grid-cols-3">{"".join(card_html)}</div>
    <section class="mt-12 grid gap-4 lg:grid-cols-2">
      <a href="projects/northline/" class="rounded-2xl border border-cyan-900 bg-slate-900 p-7 transition hover:-translate-y-1 hover:border-cyan-500">
        <p class="text-xs font-medium uppercase tracking-wider text-cyan-300">Capstone A</p>
        <h2 class="mt-3 text-2xl font-semibold text-white">Northline</h2>
        <p class="mt-2 text-sm font-medium text-slate-300">Secure Order Pipeline</p>
        <p class="mt-3 text-sm leading-6 text-slate-400">Accept an order, store a private receipt, route it with EventBridge, fan it out with SNS, and buffer fraud, billing, and shipping on separate queues.</p>
      </a>
      <a href="projects/clearfile/" class="rounded-2xl border border-indigo-900 bg-slate-900 p-7 transition hover:-translate-y-1 hover:border-indigo-500">
        <p class="text-xs font-medium uppercase tracking-wider text-indigo-300">Capstone B</p>
        <h2 class="mt-3 text-2xl font-semibold text-white">Clearfile</h2>
        <p class="mt-2 text-sm font-medium text-slate-300">Document Processing Pipeline</p>
        <p class="mt-3 text-sm leading-6 text-slate-400">Upload with a presigned URL, route PDF and image objects, retry through SQS, and publish DocumentReady only after the result is stored.</p>
      </a>
    </section>
    {bp.lab_shell("Which service owns this requirement?", "Answer all eight. The passing habit is to name the contract—buffer, fan-out, route, object, identity, or network—before naming the product.")}
    <footer class="mt-12 border-t border-slate-800 py-8 text-sm leading-6 text-slate-500">The drills are original teaching questions for Cloud Practitioner, Solutions Architect Associate, Developer Associate, and SysOps study. They are not official exam items. Confirm current AWS quotas and prices before relying on a number.</footer>
  </main>
  {bp.script(lab_cases)}
</body>
</html>
'''
    (ROOT / "index.html").write_text(html, encoding="utf-8", newline="\n")


def patch_nav(relative, base, current):
    file = ROOT / relative
    raw = file.read_bytes()
    crlf = b"\r\n" in raw
    text = raw.decode("utf-8").replace("\r\n", "\n")
    start = text.find("<nav ")
    end = text.find("</nav>")
    if start < 0 or end < 0:
        raise SystemExit(f"No nav in {relative}")
    end += len("</nav>")
    updated = text[:start] + bp.nav(base, current).strip() + text[end:]
    if crlf:
        updated = updated.replace("\n", "\r\n")
    file.write_bytes(updated.encode("utf-8"))


if __name__ == "__main__":
    for builder in (content.iam, content.vpc, content.s3, content.lambda_page, content.eventbridge, northline, clearfile):
        bp.render(builder())
    write_home()
    patch_nav("sqs/index.html", "../", "sqs")
    patch_nav("sns.html", "../", "sns")
    print("pages written")
