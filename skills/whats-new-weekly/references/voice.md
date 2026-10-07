# Voice guide

Static style guide for the orchestrator when writing `draft.md` in Phase 2. Read it in full before writing a word. The audience, banned words, substitutions and links come from `CONFIG.md`.

## Audience

The people in `AUDIENCE`. They do not know what a repo, a PR, or a deploy is and they should not need to. They care about what changed for customers, what changed for their own job, and whether it worked.

## Model: a product release announcement

The page follows the shape of a product release announcement, not an engineering changelog.

- A headline paragraph naming the week's theme in plain language.
- An optional header image, the headline launch's screenshot if one was captured.
- One block per item: a bold plain-language title, then 2 to 3 sentences on what changed and why it matters, then a link if the item has one.
- Short. No walls of text. Every sentence earns its place.

## The "why staff should care" test

Every item must answer one of these in its own words: what can a customer now do that they could not before, what does this fix that people were complaining about, or what does this tell the team about how the product is performing. If a candidate cannot pass this in plain language, it does not belong on the page, no matter how much engineering effort it took.

## Sentence rules

- Short, active sentences. Say who did what.
- Benefit first, mechanism second or never. "Customers can now see live order status" beats "we added a status polling service."
- No hedging filler ("it should be noted that", "in terms of"). Say the thing.
- Apply `STYLE_RULES` from `CONFIG.md` (for example no em dashes, no semicolons).

## Banned words

Never use anything in `BANNED_WORDS` in any section of the published page. Add every framework, library and language name your team uses to that list.

## Substitutions

Use the substitution table in `CONFIG.md`. When a term has no row, describe the visible result instead of naming the mechanism.

## Worked examples (invented, for format only)

**A customer-facing feature**

> **Live order tracking on the website**
> Customers can now watch their order move from packed to out for delivery without refreshing the page. It uses the same status updates our support team sees, so the answer a customer reads matches what we tell them on the phone. Try it on any open order.
>
> Try it: https://www.example.com

**A staff-benefit item**

> **Faster loading on the account page**
> The account page now opens noticeably faster on phones, especially in the evening when traffic peaks. If a customer mentioned the page felt slow last month, this is the fix.

**Before** (technical changelog line): "Refactored the auth flow to use a shared token cache across web and mobile clients, reducing redundant calls on session restore."

**After** (staff copy): "Signing back in on the app and on the website is now noticeably faster, especially for customers who open the app several times a day."

## Impact section wording

- **Attributable:** state it as a result. "Since the new profile page launched, repeat visits are up 12%." No hedging.
- **Moved but not attributable:** early signal with the caveat named. "Early signs are positive, though we cannot yet rule out last weekend's email campaign."
- **No movement:** leave it out, unless the launch was major enough that staff will ask. Then one honest sentence: "It is too early to see a clear change in repeat visits."
- Never state a number from raw analytics event names. Translate every metric into a plain description of customer behavior before it reaches the page.

## "Try it" links

Use the real production URL for web items, from the links table in `CONFIG.md`. For mobile app items never link a URL. Write "Open the app to see it" for anything already live, or "Update the app from the store" only when staff must have a specific version to see it.
