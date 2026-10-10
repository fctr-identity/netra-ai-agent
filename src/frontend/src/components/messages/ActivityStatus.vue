<template>
  <div class="live-status">
    <div class="status-line">
      <span role="status">{{ label }}</span>
      <span class="elapsed" aria-label="Elapsed time">{{ elapsed }}s</span>
    </div>
    <p v-if="elapsed >= 20" class="slow-note">Taking longer than usual. You can use Stop to cancel.</p>
  </div>
</template>

<script setup>
defineProps({ label: String, elapsed: { type: Number, default: 0 } })
</script>

<style scoped>
.live-status { padding: 10px 14px; border-top: 1px solid var(--workspace-outline, #d6dce5); background: #f7f8fc; font-size: 13px; }
.status-line { display: flex; justify-content: space-between; gap: 12px; color: var(--text-primary, #27272a); }
.elapsed { flex-shrink: 0; font-variant-numeric: tabular-nums; color: #626b79; }
.slow-note { margin: 4px 0 0; color: #626b79; }
</style>
