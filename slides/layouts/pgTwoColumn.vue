<template>
  <div class="slidev-layout pg-two-column h-full flex flex-col">
    <!-- Title Section -->
    <h1 v-if="$slots.title" class="mb-6">
      <slot name="title" />
    </h1>

    <!-- Two Column Content -->
    <div class="flex-1 grid gap-6" :style="gridStyle">
      <!-- Left Column -->
      <div class="overflow-y-auto">
        <h2 v-if="$slots['left-title']" class="text-2xl font-semibold mb-4">
          <slot name="left-title" />
        </h2>
        <div>
          <slot name="left" />
        </div>
      </div>

      <!-- Right Column -->
      <div class="overflow-y-auto">
        <h2 v-if="$slots['right-title']" class="text-2xl font-semibold mb-4">
          <slot name="right-title" />
        </h2>
        <div>
          <slot name="right" />
        </div>
      </div>
    </div>

    <!-- Optional Footer -->
    <div v-if="$slots.footer" class="mt-6">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  leftWidth: {
    type: Number,
    default: 50  // Percentage
  },
  rightWidth: {
    type: Number,
    default: 50  // Percentage
  },
  gap: {
    type: String,
    default: '1.5rem'
  }
})

const gridStyle = computed(() => ({
  gridTemplateColumns: `${props.leftWidth}fr ${props.rightWidth}fr`,
  gap: props.gap
}))
</script>

<style scoped>
/* Typography hierarchy */
.pg-two-column :deep(h3) {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
  color: var(--slidev-theme-primary, #3B82F6);
}

.pg-two-column :deep(p) {
  margin-bottom: 0.75rem;
  line-height: 1.6;
}

.pg-two-column :deep(ul),
.pg-two-column :deep(ol) {
  margin: 0.5rem 0;
  padding-left: 1.5rem;
}

.pg-two-column :deep(li) {
  margin-bottom: 0.4rem;
  line-height: 1.6;
}
</style>
