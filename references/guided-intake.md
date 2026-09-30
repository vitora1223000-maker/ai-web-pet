# Natural guidance from an idea

Use this when the user has no character image or established design. Guide the conversation in the user's language; use the fixed opening below for a blank-slate request, translating it when needed. Later examples demonstrate tone and pacing. Do not present the schema as a questionnaire or send every stage at once.

## Conversation rules

- Read what the user already supplied. Ask only missing questions, exactly one key question per turn. Wait for the answer before the next stage.
- Aim for four to six clear choices, plus a separate custom answer option. “I don't know” is a useful answer: propose two or three distinct, concise directions based on what is known, then let the user choose or combine them. Do not ask them the same question again.
- Summarize choices in ordinary language, then move forward. Fill the structured documents yourself. Names, exact colors and optional details can remain undecided; do not block concept exploration on them.
- Treat suggestions as proposals, not approved facts. “You decide” permits proposing a coherent draft, not silently approving the brief or canonical image.
- Keep frame rates, alpha, anchors, hashes and manifest fields out of the creative interview. Handle technical decisions and explain only those that affect the user's result.
- Do not promise image generation unless a usable tool is available. At the art stage, explain the available native or external handoff route using generation.md. Do not interrupt the opening conversation with model/API setup.

## Fixed user entry prompt

Publish this copyable starting prompt in the user guide and agent UI:

> 请使用 ai-web-pet 带我从零设计一只可以放在网页里的小宠物。
> 我现在没有角色图，也没有想好物种、风格、性格和配色。
> 请不要替我直接决定，每次只问我一个关键问题，并尽量给我 4～6 个清晰选项，同时保留“自定义”。
> 先把角色方向一步一步选出来，再告诉我下一步需要生成什么图片。

Equivalent wording also activates this route; do not require an exact string. For this blank-slate entry, send the single question below as the first response and wait for the user's answers. Do not initialize files or generate art before this interview response. For a user who already supplied answers, follow the skip rules rather than repeat them.

## 1. Who will accompany the user?

Fixed first response for the blank-slate entry:

 > 我们先选它是什么，其他一步一步来。你更想做哪一类小宠物？
>
> 1. 猫咪
> 2. 狗狗
> 3. 兔子、仓鼠等小动物
> 4. 小龙、精灵等幻想生物
> 5. 机器人或机械生命
> 6. 云朵、植物、食物等拟人小生命
> 7. 自定义：说说你想要的，暂时没想法也可以

Wait for the answer. If a broad category needs narrowing, ask that as the next single question. Then explore style, personality, colors/signature and intended website role one at a time, reusing anything already supplied. Each question should offer four to six relevant options plus custom input where practical. Never silently choose on the user's behalf.

If the user already says “a quiet black cat for my blog,” reuse type, color, personality and context; skip this full opening. Ask the most useful remaining visual question.

If the user says “no idea, just cute,” offer small concepts rather than more abstract questions:

> 可以从这三个方向挑感觉：一只困困的云团，平时慢慢飘；一只爱收集小东西的圆耳鼠；或者一条装得很威风、其实很黏人的小龙。哪个让你更想带回家？也可以混着选。

These are examples, not default mascots to impose on every user.

## 2. Discover the appearance

Ask each missing preference in a separate turn. The following are topic examples, not a combined response; expand the current topic into four to six clear choices plus custom input:

> 它的样子你更喜欢毛茸茸、简洁卡通、像素，还是黏土玩偶的感觉？不好想象的话，我们可以用候选图来选。
>
> 有没有喜欢的颜色或小标志？比如卷尾巴、小围巾、星星耳朵；没有的话，我会按它的性格提方案。
>
> 有什么一定不想要的？比如不要太幼、不穿衣服，或者不要像人一样站着。

Do not invent anatomy or impose accessories. Describe a proposed signature and proportions concretely if the user delegates design. Offer visual candidates when wording stops helping, through the available generation route.

After the user has selected the direction, explain which images are needed next: first a full-body canonical design candidate; after its approval, only the reference views needed for the planned actions. Do not jump straight to animation frames.

## 3. Review a short brief, then the actual character

Turn the answers into a short, readable proposal, for example:

> 我们先做一只住在博客里的安静小龙：深绿色、圆圆的身体，耳朵像小叶子，平时有点困，看到你会偷偷靠近。先按这个方向做定妆候选，可以吗？

This is the brief review, not character-lock approval. Record the exact confirmed brief revision. Build the Character Bible from the agreed choices, with proposed or unknown details clearly distinguished. Present actual design candidates using generation.md; invite concrete edits such as ears, silhouette, expression or color. A draft may change freely before lock.

When the user selects a candidate, confirm the actual canonical image and its defining features together, in plain language:

> 就用这张作为之后所有动作的标准形象，好吗？圆耳、短翅膀和尾尖的浅色斑会保持一致。

If they already explicitly approved that exact image and those unchanged features, record that evidence without asking again. A text description alone does not complete Character Lock.

## 4. Ask about actions after the character is locked

> 现在它长什么样已经定下来了。你最想先看它做什么？我们可以先选两三个：平时发呆、点它时打招呼、等结果时自己玩。你有特别想看的动作也可以直接说。

Reuse actions requested earlier. Translate the selected actions into acting beats and enter/loop/exit where appropriate using actions.md. Ask about emotional intent or contact only when it matters; do not make the user specify frame counts. A small first set is a suggestion, not a limit on explicitly requested scope.

## Route exceptions

- Existing character image or real pet photo: inspect the original and use creation.md's corresponding route; ask which visible traits must stay and how much stylization is wanted. Do not restart the idea interview.
- Rich initial brief: reflect it back for any needed approval and ask only consequential gaps; do not force multiple interview rounds.
- User only wants to see the onboarding: demonstrate the dialogue without initializing a character, generating art or marking approvals.
