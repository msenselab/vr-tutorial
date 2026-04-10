<template>
  <div
    class="p-4 rounded-lg"
    :class="[bgColor, borderClass, { 'text-center': center }]"
  >
    <div v-if="title || label" class="flex items-center gap-2 mb-2">
      <component v-if="icon" :is="icon" class="w-5 h-5" />
      <strong class="text-base">{{ title || label }}</strong>
    </div>
    <div :class="textClass">
      <slot />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  // Content props
  title: String,
  label: String,  // Alternative to title for backwards compatibility

  // Style props
  bgColor: {
    type: String,
    default: 'bg-blue-50'
  },
  border: {
    type: String,  // 'left', 'all', 'none'
    default: 'none'
  },
  borderColor: {
    type: String,
    default: 'border-blue-400'
  },

  // Layout props
  center: {
    type: Boolean,
    default: false
  },
  textSize: {
    type: String,
    default: 'text-sm'
  },

  // Icon (optional)
  icon: String
})

const borderClass = computed(() => {
  if (props.border === 'left') {
    return `border-l-4 ${props.borderColor}`
  } else if (props.border === 'all') {
    return `border-2 ${props.borderColor}`
  }
  return ''
})

const textClass = computed(() => props.textSize)
</script>

<style scoped>
/* Additional styling if needed */
</style>
