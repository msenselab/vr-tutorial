<template>
  <div class="slidev-layout pg-three-block h-full flex flex-col">
    <!-- Title Section -->
    <h1 v-if="$slots.title" class="mb-6">
      <slot name="title" />
    </h1>

    <!-- Three Block Grid -->
    <div class="flex-1 grid grid-cols-3 gap-6">
      <!-- Block 1 -->
      <div class="p-6 rounded-lg shadow-md" :class="color1">
        <h3 v-if="$slots['block1-title']" class="text-base font-bold mb-2">
          <slot name="block1-title" />
        </h3>
        <div class="text-sm">
          <slot name="block1" />
        </div>
      </div>

      <!-- Block 2 -->
      <div class="p-6 rounded-lg shadow-md" :class="color2">
        <h3 v-if="$slots['block2-title']" class="text-base font-bold mb-2">
          <slot name="block2-title" />
        </h3>
        <div class="text-sm">
          <slot name="block2" />
        </div>
      </div>

      <!-- Block 3 -->
      <div class="p-6 rounded-lg shadow-md" :class="color3">
        <h3 v-if="$slots['block3-title']" class="text-base font-bold mb-2">
          <slot name="block3-title" />
        </h3>
        <div class="text-sm">
          <slot name="block3" />
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
const props = defineProps({
  color1: {
    type: String,
    default: 'bg-blue-100'
  },
  color2: {
    type: String,
    default: 'bg-green-100'
  },
  color3: {
    type: String,
    default: 'bg-orange-100'
  }
})
</script>

<style scoped>
.pg-three-block :deep(ul) {
  margin: 0.5rem 0;
  padding-left: 1.25rem;
}

.pg-three-block :deep(li) {
  margin-bottom: 0.3rem;
  line-height: 1.4;
}

.pg-three-block :deep(p) {
  margin-bottom: 0.5rem;
  line-height: 1.4;
}
</style>
