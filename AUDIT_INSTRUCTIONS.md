# How to Complete the detect-secrets Audit

## Current Status
The `detect-secrets audit` command is currently running in your terminal and waiting for your input.

## What You See
The audit interface is showing:
- **File**: `docs/source/modules/zos_backup_restore.rst`
- **Line**: 66
- **Secret Type**: Secret Keyword
- **Flagged Text**: `*auth=true*` (the word "auth" triggered the detector)

## What to Do Now

### Step 1: Mark as False Positive
In the terminal where the audit is running, you'll see a prompt asking if this is a real secret.

**Press `n`** (for "No") to mark this as a false positive, since this is just documentation text explaining the `auth=true` parameter.

### Step 2: Save and Exit
After pressing `n`, the audit will ask if you want to save.

**Press `s`** (for "Save") to save your audit decision to the `.secrets.baseline` file.

### Step 3: Verify
After the audit completes, verify that the issue is resolved by running:
```bash
cd ibm_zos_core
detect-secrets scan --baseline .secrets.baseline
```

This should now pass without any unaudited secrets.

## Expected Result
After completing the audit:
- The `.secrets.baseline` file will be updated
- The secret at line 66 will be marked as `"is_verified": false` (meaning it's not a real secret)
- Future scans will not flag this as an unaudited secret
- The CI/CD pipeline should pass

## Why This is a False Positive
The text `*auth=true*` is documentation explaining a module parameter. It's not an actual authentication credential or secret. The KeywordDetector plugin flagged it because it contains the word "auth", but in this context, it's completely safe.