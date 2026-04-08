---
name: contact-list
description: "Single source of truth for all contacts, PAs, and WhatsApp groups. Use when: looking up a phone number, email, address, PA, group JID, adding/updating a contact, or before sending any WhatsApp message. Reads and writes contact-list.md in the workspace root."
---

# Contact List Skill

## Minimum Model
Any model. This is a lookup/edit skill.

---

## Source File

All contact data lives in **`contact-list.md`** (workspace root). This is the ONLY source of truth for contacts, PAs, and groups.

### Recommended File Structure

```markdown
<!-- LOAD THIS FILE when: looking up a contact, phone, email, address, PA, group JID, or sending a WhatsApp message. -->

# Contacts, PAs & Groups

## Contacts

| Name | Phone | Email | Address | City | Owner Role | PA | Notes |
|---|---|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | leadership | PA_Name (+phone) | ... |

## Active PAs

| PA Name | PA Phone | Owner | Owner Phone | Status | Notes |
|---|---|---|---|---|---|
| ... | ... | ... | ... | ✅ Active | ... |

## PA Sync List

### DM Targets
- +XXXXXXXXXXX — PA_Name (Owner)

### Group Targets
- XXXXXXXXXXX@g.us — Group Name

## WhatsApp Groups

| Group Name | Group JID | Notes |
|---|---|---|
| ... | XXXXXXXXXXX@g.us | ... |
```

### Key fields

- **Owner Role**: set to `leadership` for leadership/directors. Leave empty otherwise.
- **PA**: `PA_Name (+phone)` if the contact has a PA agent. Empty otherwise.
- **Status** (in Active PAs): `✅ Active`, `🔧 Setup`, `❌ Inactive`

---

## Lookup

### Find a contact by name

```bash
grep -i "SEARCH_TERM" contact-list.md
```

Replace `SEARCH_TERM` with the name (partial match OK, case-insensitive).

### Find a PA by owner name

```bash
grep -i "OWNER_NAME" contact-list.md | head -5
```

The PA column in the contacts table shows `PA_NAME (+phone)`. The Active PAs section has the full mapping.

### Find a group JID

```bash
grep -i "GROUP_NAME" contact-list.md
```

Look in the WhatsApp Groups section (bottom of file).

### Pre-send validation

Before sending any WhatsApp message:
1. `grep` the recipient's name or phone in `contact-list.md`
2. Verify the phone/JID exists
3. If not found → ask the owner. **Never guess a phone number or JID.**

---

## Add a Contact

Append a new row to the **Contacts** table in `contact-list.md`:

```
| Name | Phone | Email | Address | City | Owner Role | PA | Notes |
```

Rules:
- Check for duplicates first: `grep -i "NAME_OR_PHONE" contact-list.md`
- If the contact is from leadership → set `Owner Role` = `leadership`
- If they have a PA → fill the PA column with `PA_NAME (+phone)`
- Keep alphabetical order
- After adding → `git add contact-list.md && git commit -m "add contact: NAME" && git push`

---

## Update a Contact

1. Read `contact-list.md`
2. Find the row to update
3. Edit the specific field (phone, address, PA, etc.)
4. After updating → `git add contact-list.md && git commit -m "update contact: NAME — FIELD" && git push`

---

## Add a New PA

When a new PA is onboarded:

1. **Add to Active PAs table** — new row with PA Name, Phone, Owner, Owner Phone, Status
2. **Update the contact row** — add PA name + phone to the PA column of the owner's entry
3. **Add to PA Sync List** — append DM target line: `- +PHONE — PA_NAME (Owner)`
4. **Git push** — `git add contact-list.md && git commit -m "add PA: PA_NAME for OWNER" && git push`

---

## Add a New Group

When joining a new WhatsApp group:

1. Add a row to the WhatsApp Groups table
2. Include: Group Name, Group JID, Notes
3. Git push

---

## Remove / Deactivate

- **Contact removed:** Delete the row. Git push.
- **PA deactivated:** Change status to `❌ Inactive` in Active PAs. Remove from PA Sync List DM targets. Clear the PA column in the contact row. Git push.

---

## Trigger Phrases

| If the owner says... | Action |
|---|---|
| "who is X" / "tell me about X" | Lookup by name |
| "phone for X" / "X's number" | Lookup phone |
| "address for X" | Lookup address |
| "email for X" | Lookup email |
| "X's PA" / "find PA for X" | Lookup PA |
| "group JID" / "JID for X" | Lookup group |
| "add contact" | Add contact flow |
| "update contact" / "change phone for X" | Update contact flow |
| "new PA" / "PA onboarded" | Add PA flow (then also run ai-pa) |

---

## Integration with Other Skills

- **ai-pa**: After looking up a contact here, use ai-pa for PA-to-PA coordination
- **pa-onboarding**: After onboarding completes, use this skill to register the new PA
- **meetings**: Before scheduling, use this skill to find the other PA's contact
- **whatsapp**: Before sending any message, validate the phone/JID here

---

## Cost Tips

- **Very cheap** — grep + file edit, any model works
- **No API calls** — everything is local markdown
- Batch multiple updates into one commit

---

## Error Reference

| Error | Cause | Fix |
|---|---|---|
| Contact not found | Name spelling, partial match | Try shorter search term, check alternate spellings |
| Duplicate detected | Contact already exists | Update existing row instead of adding |
| File not found | `contact-list.md` missing | Check workspace root, run `git pull` |
| Git push failed | Network or auth issue | Retry, check git credentials |
