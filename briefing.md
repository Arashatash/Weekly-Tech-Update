# Weekly AI Strategy Briefing — Week 29, Jul 13 – Jul 19, 2026

> Capital and code converge on the same conclusion: AI's next trillion is agents that ship revenue, not models that ship demos.

This week the AI narrative shifted from 'is it real' to 'who captures value now that it is.' Top-tier capital (Sequoia, a16z, Founders Fund) is deploying against two crisp theses — services-as-software and agent-native infrastructure — while operators (OpenAI, Google, DoorDash, Framer) shipped concrete products that assume agents are first-class users. Simultaneously, open-weight frontier releases (Kimi K3) and inference constraints at OpenAI make it clear the moat is no longer the model itself.

---

## Capital & Theses

### Services-as-Software: AI Eats Labor Budgets
**Source:** Sequoia Capital | **Signal:** high

Sequoia is reframing the AI opportunity from selling software seats to replacing services P&L. The thesis: verticalized AI agents that book revenue like SaaS but attack the multi-trillion-dollar labor market (wealth mgmt, retail ops, healthcare admin) — see partnerships with Nevis (wealth), Bunkerhill Health, and the $1T retail Amazon-successor essay. Capital is rotating from horizontal foundation-model bets into domain-native agent companies.

[Read more →](https://sequoiacap.com/article/services-the-new-software/)

---

### Agent-Native Infrastructure Stack
**Source:** a16z | **Signal:** high

a16z is triangulating a full infra stack purpose-built for AI agents, not humans: Exa (search), plus new investments in Netris, Runta, Convey and Town. DoorDash launching dd-cli for agents this week and Google exposing AI Mode as an app-linking surface confirm the direction. Investable wedge: retrieval, memory, identity, payments and observability layers that assume a non-human primary user.

[Read more →](https://a16z.com/podcast/building-search-for-ai-agents-with-exa-ceo-will-bryk/)

---

### Open Frontier Models Compress the Moat
**Source:** Y Combinator | **Signal:** high

Kimi K3 (front-page HN, 968 pts) plus Ring-Zero's trillion-parameter open RL work and LM Studio Bionic's local-agent runtime signal that open-weight frontier capability is now weeks, not quarters, behind closed labs. Implication for investors: model layer margins compress further; value accrues to distribution, workflow lock-in, proprietary data and inference infrastructure.

[Read more →](https://www.kimi.com/blog/kimi-k3)

---

### AI Safety as Product Feature, Not Just Policy
**Source:** MIT Technology Review | **Signal:** medium

OpenAI's GPT-Red (adversarial LLM sparring partner) and Anthropic's interpretability breakthrough are shifting safety from a compliance line-item to a differentiator that gates enterprise deals and government approvals (see GPT-5.6's staggered release). Capital thesis: red-teaming, interpretability tooling, and evals infrastructure become fundable standalone categories.

[Read more →](https://www.technologyreview.com/2026/07/15/1140514/meet-gpt-red-an-llm-super-hacker-openai-built-to-make-its-models-safer/)

---

### Consumer AI Wraps Real Wallets
**Source:** TechCrunch | **Signal:** medium

Fora hitting $1B on a $60M Forerunner/Tactile round proves AI-enabled service marketplaces (not pure software) can generate SaaS-like multiples. Combined with Uber's $14.8B Delivery Hero deal and Roblox's prompt-to-game feature, capital is validating that AI is a distribution accelerant for real-world transactions — not a standalone product category.

[Read more →](https://techcrunch.com/2026/07/16/ai-powered-travel-agency-fora-hits-unicorn-status-raises-60m/)

---

## What's Being Built

### Kimi K3: Open Frontier Intelligence
**Source:** Y Combinator | **Signal:** high

Moonshot's Kimi K3 landed at 968 HN points, positioning as an openly available frontier-tier model. For operators, this is the second time this quarter an open model has meaningfully closed the gap on GPT/Claude — accelerating the shift of value from weights to workflow, data and inference infra.

[Read more →](https://www.kimi.com/blog/kimi-k3)

---

### GPT-Red: OpenAI's In-House LLM Adversary
**Source:** MIT Technology Review | **Signal:** high

OpenAI built a dedicated adversarial 'super-hacker' LLM that trains against GPT-5.6 to harden it against cyberattacks. Signals that frontier labs now run internal red-team models as first-class product infrastructure — a template competitors and safety-focused startups will replicate.

[Read more →](https://www.technologyreview.com/2026/07/15/1140514/meet-gpt-red-an-llm-super-hacker-openai-built-to-make-its-models-safer/)

---

### Google AI Mode Becomes an App-Linking Agent Surface
**Source:** TechCrunch | **Signal:** high

Google is pushing AI Mode from Q&A into task completion across linked apps, and rebranding NotebookLM to Gemini Notebook to consolidate the Gemini surface. Strategic read: Google is racing to make Search the default agent runtime for consumers before OpenAI or Anthropic claim that layer.

[Read more →](https://techcrunch.com/2026/07/16/googles-ai-mode-now-lets-you-link-and-interact-with-select-apps/)

---

### DoorDash Ships CLI for AI Agents
**Source:** TechCrunch | **Signal:** high

dd-cli is a limited beta letting developers and AI agents place DoorDash orders from a terminal — an explicit acknowledgment that software is now being designed for agent consumption first. Every consumer marketplace will need an agent-facing API within 12 months or lose intent capture.

[Read more →](https://techcrunch.com/2026/07/16/yes-you-can-now-order-doordash-from-the-command-line/)

---

### Framer AI Agents (Product Hunt launch)
**Source:** Product Hunt | **Signal:** high

Validates Agent-Native Infrastructure Stack: Framer shipped on-canvas AI agents that design, write, and organize sites, and can plug into external agents like Claude Code or Codex. This is a live example of an existing SaaS retooling its surface for agents as first-class users — exactly the wedge a16z is funding across Exa, Netris and Town.

[Read more →](https://www.producthunt.com/leaderboard/daily/2026/7/15)

---

### LM Studio Bionic: Local Agent Runtime for Open Models
**Source:** Y Combinator | **Signal:** medium

LM Studio launched Bionic, an AI agent runtime aimed at open-weight models running locally. Confirms that open-source frontier + local inference is now a shippable stack for privacy-sensitive and cost-sensitive enterprise use cases — a direct threat to closed-model API monetization.

[Read more →](https://lmstudio.ai/blog/introducing-lm-studio-bionic)

---

### Stigg 2.0 — Usage Runtime for AI Products (Product Hunt)
**Source:** Product Hunt | **Signal:** medium

Validates Services-as-Software: AI Eats Labor Budgets: Stigg 2.0 is a usage-metering runtime purpose-built for AI products where cost is variable per token/action. As Sequoia's services-as-software thesis takes hold, AI companies need metering that maps to labor-value outputs, not seats — Stigg operationalizes exactly that infra gap.

[Read more →](https://www.producthunt.com/products/stigg-2)

---

## Opportunities Now

### Build the agent-facing API layer for legacy marketplaces
**Source:** TechCrunch | **Signal:** high | **Horizon:** 0-6 mo

DoorDash's dd-cli is a template every marketplace/SaaS must copy this quarter. Who wins: infra startups offering 'agent-mode' SDKs (auth, cart, checkout, refunds) to Instacart/Uber Eats/Shopify tier merchants. What must be true: MCP or similar standard consolidates; merchants accept that agents become 15%+ of intent within 12 months.

[Read more →](https://techcrunch.com/2026/07/16/yes-you-can-now-order-doordash-from-the-command-line/)

---

### N71 — Shared Context for AI Agents (Product Hunt)
**Source:** Product Hunt | **Signal:** high | **Horizon:** 0-6 mo

Validates Agent-Native Infrastructure Stack: N71 gives all your AI agents one shared context — a memory/state primitive that agent-heavy shops need this quarter. Operators running multiple copilots (Cursor + Claude Code + Codex) can adopt immediately; investors should map who owns 'agent memory' before it consolidates.

[Read more →](https://www.producthunt.com/products/n71)

---

### Vertical AI travel/services rollups
**Source:** TechCrunch | **Signal:** high | **Horizon:** 0-6 mo

Fora's $1B mark validates the AI-augmented agent-network model in travel. Replicable now in insurance broking, real-estate transactions, small-business bookkeeping. Who captures: operators with existing agent networks who bolt on AI, not pure-software startups. Must be true: fragmented services markets, human trust still gates the transaction, AI drops per-agent COGS by 40%+.

[Read more →](https://techcrunch.com/2026/07/16/ai-powered-travel-agency-fora-hits-unicorn-status-raises-60m/)

---

### AI-generated content provenance & payout routing
**Source:** TechCrunch | **Signal:** medium | **Horizon:** 0-6 mo

X is using Grok to redirect creator payouts to original authors and demote engagement bait — a first mainstream monetization tie between provenance detection and revenue. Opportunity: cross-platform provenance/attribution APIs sold to YouTube, TikTok, Substack, Beehiiv. Window: 6 months before platforms build in-house.

[Read more →](https://techcrunch.com/2026/07/16/x-cracks-down-on-creators-who-steal-content/)

---

## Opportunities Mid-term

### AI in wealth & healthcare vertical agents
**Source:** Sequoia Capital | **Signal:** high | **Horizon:** 6-18 mo

Sequoia is publicly backing Nevis (wealth) and Bunkerhill Health (patient outcomes) as agent-driven category winners. Mid-term wedge (6-18m): startups replacing 30-50% of RIA back-office, radiology triage, and specialty-clinic ops. Must be true: regulator comfort with AI-in-the-loop, integrated data access, and a services-margin business model. Who wins: teams with domain operators + strong distribution partnerships.

[Read more →](https://sequoiacap.com/article/nevis-bringing-ai-to-wealth-management/)

---

### Interpretability-as-a-Service for regulated enterprises
**Source:** MIT Technology Review | **Signal:** medium | **Horizon:** 6-18 mo

Anthropic's interpretability research gives concrete signals about model internals. In 12-18 months, enterprises in banking, health and gov procurement will require interpretability artifacts alongside model outputs. Startups shipping 'explainability layers' for third-party models can capture a compliance-driven category before Anthropic/OpenAI ship native alternatives.

[Read more →](https://www.technologyreview.com/2026/07/13/1140343/what-anthropics-latest-ai-discovery-does-and-doesnt-show/)

---

### Personalized AI avatar rights & talent management
**Source:** TechCrunch | **Signal:** medium | **Horizon:** 6-18 mo

Google Vids letting anyone star as their own AI avatar plus Gemini Omni pushes personal likeness into mainstream commercial workflows. Mid-term opportunity: rights management, likeness-licensing marketplaces, and enterprise avatar-governance tooling. Must be true: legal frameworks harden and enterprises want auditable consent for internal-video use.

[Read more →](https://techcrunch.com/2026/07/16/google-vids-now-lets-you-star-in-your-own-ai-videos/)

---

### Prompt-to-experience creation platforms beyond gaming
**Source:** TechCrunch | **Signal:** medium | **Horizon:** 6-18 mo

Roblox's Build feature turns a single prompt into a playable game on mobile. In 12-18 months the same primitive lands in training simulations, retail configurators, and edtech. Winners: infra players enabling prompt-to-3D across engines, plus category-native studios who own distribution to specific user cohorts (kids, enterprise trainers).

[Read more →](https://techcrunch.com/2026/07/16/roblox-launches-an-ai-powered-game-creation-feature-in-its-mobile-app/)

---

## Opportunities Long-term

### Sub-frontier open models as commodity utility
**Source:** Y Combinator | **Signal:** high | **Horizon:** 18+ mo

Kimi K3, Ring-Zero and other trillion-parameter open efforts trend toward a world where frontier-tier reasoning is a commoditized utility priced like electricity. 18+ months: opportunity is in the layers that monetize proprietary data, workflow lock-in, and hyper-vertical fine-tuning. Foundation-model bets without a data or distribution moat lose value.

[Read more →](https://www.kimi.com/blog/kimi-k3)

---

### Photonic & specialized compute breaking Nvidia's grip
**Source:** MIT Technology Review | **Signal:** medium | **Horizon:** 18+ mo

PsiQuantum's photonic quantum plan plus continued momentum in optical/analog AI accelerators signals a real path to non-GPU compute at scale by 2028+. Long-horizon bet: startups building software stacks portable across GPU/photonic/quantum backends will capture margin as substrate diversifies. Must be true: at least one non-CUDA stack achieves production reliability.

[Read more →](https://www.technologyreview.com/2026/07/14/1140356/psiquantum-plan-massive-quantum-computer-out-of-light/)

---

### World-models as a distinct product layer
**Source:** MIT Technology Review | **Signal:** medium | **Horizon:** 18+ mo

Coverage of world models as a rising research frontier suggests LLMs plateau as pure language systems and physical/temporal reasoning becomes the next platform. 18+ months: startups embedding world-model reasoning into robotics, logistics, and simulation win category positions before frontier labs bundle it. Directional bet — outcome depends on whether world models deliver embodied gains vs. remaining research-lab curiosities.

[Read more →](https://www.technologyreview.com/2026/07/14/1140391/the-download-anthropic-claude-internal-thoughts-world-models/)

---

### Global AI governance regime creates compliance category
**Source:** MIT Technology Review | **Signal:** medium | **Horizon:** 18+ mo

Altman's FT op-ed proposing an IAEA-style AI body plus OpenAI's staged GPT-5.6 release under US Commerce oversight point to a real governance regime forming by 2028. Long-horizon opportunity: eval/audit/attestation businesses selling to labs and governments; export-control-compliant deployment tooling. Depends on whether US, EU and China converge on shared standards vs. bifurcate.

[Read more →](https://www.technologyreview.com/2026/07/16/1140600/the-download-openai-unveils-gpt-red-heat-pumps-rise-us/)

---

## Leader Voices

### Sam Altman — OpenAI
**Stance:** Bullish

In an FT op-ed and follow-up interviews, Altman argued AI will reshape material conditions of human life on a scale not seen since electricity, and called for a US-led international forum modelled on the IAEA to set global AI standards.

Altman is repositioning OpenAI as a policy-setter, not just a lab. Operators should expect standards, staged releases, and eval requirements to become non-negotiable for enterprise and gov deals within 12 months.

[Source →](https://siliconangle.com/2026/07/02/sam-altman-calls-us-led-international-forum-set-global-ai-standards/)

---

### Sam Altman — OpenAI
**Stance:** Bullish

Altman posted that GPT-5.6 Sol's growth is 'insane', that the inference team has done 'heroic work', and warned there may be 'hiccups' as OpenAI scales capacity — while separately mocking Musk's orbital data-center pitch.

Frontier inference is capacity-constrained even at OpenAI. Alternative inference providers, distillation stacks, and open-weight local runtimes have a real window to win overflow demand this quarter.

[Source →](https://www.axios.com/2026/07/14/sam-altman-chat-gpt-sol-ultra-warning)

---

### Marc Andreessen — a16z
**Stance:** Bullish

On the a16z podcast this week, Andreessen argued the consumer surplus generated by AI is already massive and largely uncaptured, and reframed founder evaluation around who can convert that surplus into durable enterprise value.

a16z's operating thesis: consumer AI is under-monetized. Expect concentrated bets on founders capable of building distribution and monetization on top of commoditizing model layers.

[Source →](https://a16z.com/podcast/marc-andreessen-on-evaluating-founders-and-ais-consumer-surplus-2/)

---

### Roelof Botha / Sequoia partners — Sequoia Capital
**Stance:** Bullish

In this week's 'Services: The New Software' essay and the '$10 Trillion AI Revolution' video, Sequoia argued the addressable market for AI is labor budgets, not software budgets, and highlighted portfolio bets (Nevis, Bunkerhill, Sable) that book revenue on services outcomes.

Sequoia is anchoring its 2026 AI thesis on services-as-software. Founders pitching horizontal AI tooling will face higher bars; verticalized outcome-priced companies will get preferred terms.

[Source →](https://sequoiacap.com/article/services-the-new-software/)

---

### Elon Musk — SpaceX / xAI
**Stance:** Bullish

Musk released Grok 4.5 alongside OpenAI's GPT-5.6 and continued to promote orbital AI data centers as a solution to Earth-side energy limits, drawing a public rebuke from Altman that the timeline is unrealistic.

xAI's Grok 4.5 undercuts GPT-5.6 on cost for coding workflows. Enterprise buyers should benchmark multi-model; investors should treat orbital data centers as narrative, not near-term capex.

[Source →](https://www.forbes.com/sites/antoniopequenoiv/2026/07/11/sam-altman-says-elon-musk-is-obsessed-with-him-in-boast-about-latest-gpt-model/)

---

### Dario Amodei — Anthropic
**Stance:** Neutral

Amodei publicly proposed AI regulation modeled on the FAA and Anthropic released new interpretability research surfacing a 'hidden space' where Claude puzzles over concepts, positioning the company on safety leadership at a ~$1T valuation.

Anthropic is turning interpretability into a marketing and regulatory moat. Expect enterprise procurement to increasingly require interpretability artifacts — a category opportunity for third-party tools.

[Source →](https://www.technologyreview.com/2026/07/13/1140343/what-anthropics-latest-ai-discovery-does-and-doesnt-show/)

---

### Will Bryk — Exa
**Stance:** Bullish

On the a16z podcast, Exa CEO Will Bryk argued that search for AI agents is a fundamentally different product from search for humans and that the retrieval layer will be one of the highest-leverage picks-and-shovels businesses of the next 5 years.

Retrieval and search purpose-built for agents is emerging as a discrete category. Builders should not assume Google-style search is fit-for-purpose in agent stacks; investors should scan for competitors before Exa consolidates the layer.

[Source →](https://a16z.com/podcast/building-search-for-ai-agents-with-exa-ceo-will-bryk/)

---

### Brian Halligan — HubSpot (ex-CEO)
**Stance:** Neutral

In a Sequoia-published essay this week, Halligan distilled his zero-to-$25B journey into repeatable operating lessons for founders scaling AI-era companies through the awkward middle stage.

As AI-native companies hit scale-up velocity faster than prior generations, operator playbooks like Halligan's become premium content. Boards should adopt structured scaleup practices earlier than in the 2010s SaaS wave.

[Source →](https://sequoiacap.com/article/a-startup-founder-to-scaleup-ceos-journey-from-0-to-25billion-halliganisms/)

---

## Commentary Synthesis: Investors vs Operators

This week the AI market split cleanly along two axes. On the capital side, Sequoia and a16z stopped debating whether AI is real and started deploying against two adjacent theses: agents-as-services (verticalized AI that eats labor P&L) and agent-native infrastructure (search, memory, payments, and identity for a non-human user). On the operator side, OpenAI, Google, and DoorDash pushed the same conclusion into product: OpenAI is training internal adversarial models to harden GPT-5.6, Google is turning AI Mode into a task-completion surface, and DoorDash is exposing a CLI so agents can transact. Meanwhile Kimi K3 and LM Studio Bionic show open-weight frontier + local runtime is now a shippable enterprise stack, which compresses model-layer margins. The honest read: hype has cooled into execution. Value is accruing to distribution, proprietary data, workflow lock-in, and inference infrastructure — not to model weights alone. The next 12 months' interesting battles are agent identity/payments, safety-as-differentiator (GPT-Red style), and services-as-software rollups in wealth, healthcare, and travel. Expect governance to become a real product constraint before it becomes a moat.

| Topic | Investor View | Operator View | Practical Implication |
|---|---|---|---|
| **Where AI value accrues next** | Sequoia is pushing that services (not software) are the next $10T category — vertical agents that book revenue against labor budgets, not seat licenses. | Sam Altman is signaling continued frontier scaling (GPT-5.6 Sol demand 'insane') and framing OpenAI as the horizontal platform on which services get built. | *Founders should stop trying to be the next foundation lab and instead pick a services vertical where AI can compress cost-of-delivery 40%+ this year.* |
| **Open vs closed frontier models** | a16z is investing across agent infra assuming a plural model layer (Exa, Netris, Town) — implicit bet that model choice becomes a runtime decision. | OpenAI and Anthropic keep raising frontier bars and locking distribution via consumer + gov channels; Altman calls for an IAEA-style body that would advantage incumbents. | *Assume a multi-model future in your architecture; do not build critical differentiation on a single API. Track Kimi K3-tier open releases monthly.* |
| **Safety and governance** | Investors increasingly treat interpretability and red-team tooling as fundable categories (see Anthropic research coverage; growing eval/audit deal flow). | Altman is publicly advocating a governance framework and OpenAI accepted staged GPT-5.6 release under Commerce Dept review — safety is now a product gating factor. | *Any enterprise-facing AI product needs an evals + red-team + interpretability story on the roadmap; expect procurement to demand it within 12 months.* |
| **Where compute goes** | VCs are quietly funding non-GPU stacks (photonic, quantum, custom silicon) as long-horizon bets against Nvidia monoculture. | Altman publicly mocked SpaceX's orbital data-center pitch; operators still see 100% of near-term compute happening in earthbound GPU/ASIC data centers. | *Plan for GPU scarcity through 2027 in near-term. Non-GPU compute is a 3-5 year bet, not a 2026 procurement option.* |

---

## Follow the Money

| Trend Type | Observation | Implication |
|---|---|---|
| **Capital Flow** | Fora raised $60M Series D at $1B valuation, led by Forerunner and Tactile Ventures — an AI-augmented travel agent network, not a pure software play. | Capital is pricing AI-augmented human-service networks with SaaS multiples. Expect more $1B+ rounds in insurance, real estate and specialty healthcare on the same template. |
| **Acquisition Or Bet** | Uber announced a $14.8B all-stock acquisition of Delivery Hero, nearly doubling global footprint. | Consolidation in delivery under an AI-agent-ready operator. Whoever owns the aggregated intent layer becomes the interface every agent framework must integrate — read this as Uber positioning to be an agent-endpoint monopoly outside China. |
| **Enterprise Spend** | OpenAI staggered GPT-5.6 release under Trump administration review, with 'many changes' before general availability. | Enterprise/government-gated release windows now shape frontier lab economics. Compliance and evals become a real line item in AI budgets — capital should flow to eval, red-team, and attestation vendors. |
| **Infra Spend** | Altman warned GPT-5.6 Sol demand growth is 'insane' with likely 'hiccups' — infrastructure team openly struggling to scale inference. | Even best-capitalized labs are inference-constrained. Alternative inference providers, distillation vendors, and local-run stacks (LM Studio Bionic, Kimi K3) benefit from the overflow. Expect $B+ inference-capacity deals through year-end. |
| **Capital Flow** | Founders Fund hired ex-OpenAI VP Ryan Beiermeister as partner; a16z announced a fresh batch of 7 AI investments (Runta, Netris, Mirendil, Probook, Prosper AI, Telepatia, Convey, Town, Lassie). | Tier-1 firms are staffing up ex-frontier-lab operators as investing partners and deploying in bulk. Signal that pipeline is deep, but also that the top decile of firms will crowd out generalist VCs from the best AI deals. |
| **Overheated Signal** | Michael Burry disclosed new AI short bets citing 'Beginning of the End'; oil major BP shut its 20-year corporate venture arm citing lackluster returns. | Skeptical capital is starting to size public shorts against AI infrastructure names, and non-strategic corporate LPs are exiting venture. Watch for a repricing event in mid-tier AI names in H2 — froth is still concentrated but the shorts are lining up. |
| **Infra Spend** | PsiQuantum publicly detailed a photonic quantum data-center plan; Altman/Musk feud spotlighted SpaceX's space-based AI data-center proposal. | Exotic compute (photonic, orbital) is being pitched to public and private capital as a hedge against GPU scarcity. Near-term this is narrative fuel; real capex still routes to conventional GPU data centers. |
| **Enterprise Spend** | Google rolled AI Mode into apps and rebranded NotebookLM to Gemini Notebook; Beehiiv, Roblox, X and Google Vids all shipped material AI features in a single week. | Every consumer platform is racing to be an agent-ready surface. Enterprise SaaS budgets will follow within 2-3 quarters; expect a wave of 'agent-mode' pricing SKUs by Q1 2027. |

---

## Top Signals

### 1. DoorDash exposes a CLI for AI agents — commerce goes agent-native
**Urgency:** Act now

First mainstream consumer marketplace to publicly ship an agent-first interface. Every peer (Instacart, Amazon, Uber Eats, Shopify) is now on the clock. Operators should audit their own agent-readiness this quarter.

### 2. Kimi K3 and Ring-Zero push open frontier within weeks of closed labs
**Urgency:** Act now

Model-layer margins are compressing faster than expected. Any company relying on model access as its primary moat should re-underwrite the thesis now. Winners rotate to data, distribution, and inference infra.

### 3. OpenAI's GPT-Red plus staged GPT-5.6 release make safety a procurement gate
**Urgency:** Stay informed

Adversarial in-house LLMs and Commerce Dept oversight of frontier releases signal that safety infrastructure is now shipping product, not policy talk. Enterprises will start demanding evals/red-team artifacts within 12 months.

### 4. Fora hits $1B and Uber buys Delivery Hero for $14.8B — capital rewards AI-augmented services
**Urgency:** Watch closely

Services-as-software is being priced like SaaS. Every fragmented professional-services vertical (insurance, RE, healthcare admin, bookkeeping) is a candidate for the same playbook. Operators with existing networks + AI overlay hold the whip hand.

### 5. Altman calls for IAEA-style AI governance while Musk/Altman feud spotlights compute politics
**Urgency:** Watch closely

Formal AI governance is coming, and frontier labs are actively shaping it. Startups should assume export controls, staged releases and eval requirements land within 24 months. Compliance tooling is a real category.
