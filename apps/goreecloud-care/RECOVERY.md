# Recovery and Rollback

Cache and temporary-file deletion is generally recreatable but is still destructive, so GoreeCloud Care previews it first. Trash emptying is permanent and has no application-level restore; the UI explicitly says so before execution. APT cache cleanup removes downloaded package archives, which may be downloaded again from configured repositories. Memory-cache reclaim changes no durable user data.

Package rollback is currently limited to uninstalling the Development package and reinstalling a previously retained package artifact. Target-device upgrade/rollback validation remains required before RC.
