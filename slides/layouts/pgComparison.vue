<template>
  <div class="slidev-layout pg-comparison h-full flex flex-col">
    <!-- Title Section -->
    <h1 v-if="$slots.title" class="mb-6">
      <slot name="title" />
    </h1>

    <!-- Comparison Grid -->
    <div class="flex-1 grid grid-cols-2 gap-6">
      <!-- Left Side -->
      <div class="p-6 rounded-lg shadow-md" :class="leftColor">
        <h3 v-if="$slots['left-title']" class="text-lg font-bold mb-3">
          <slot name="left-title" />
        </h3>
        <div class="text-sm">
          <slot name="left" />
        </div>
      </div>

      <!-- Right Side -->
      <div class="p-6 rounded-lg shadow-md" :class="rightColor">
        <h3 v-if="$slots['right-title']" class="text-lg font-bold mb-3">
          <slot name="right-title" />
        </h3>
        <div class="text-sm">
          <slot name="right" />
        </div>
      </div>
    </div>

    <!-- Optional Callout/Footer -->
    <div v-if="$slots.callout || $slots.footer" class="mt-6">
      <slot name="callout" />
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  leftColor: {
    type: String,
    default: 'bg-blue-100'
  },
  rightColor: {
    type: String,
    default: 'bg-orange-100'
  }
})
</script>

<style scoped>
.pg-comparison :deep(ul) {
  margin: 0.5rem 0;
  padding-left: 1.25rem;
}

.pg-comparison :deep(li) {
  margin-bottom: 0.4rem;
  line-height: 1.5;
}

.pg-comparison :deep(p) {
  margin-bottom: 0.5rem;
  line-height: 1.5;
}

.pg-comparison :deep(strong) {
  font-weight: 600;
}
</style>
