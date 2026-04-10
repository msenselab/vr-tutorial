<template>
  <figure class="flex flex-col items-center" :style="wrapperStyle">
    <div class="relative" :style="imageContainerStyle">
      <img
        :src="src"
        :alt="alt || caption"
        class="mx-auto"
        :style="imageStyle"
      />
    </div>
    <figcaption
      v-if="caption"
      class="mt-3 text-sm text-gray-600 text-center"
      :class="captionClass"
    >
      <span v-if="footnoteNumber" class="text-xs align-super mr-1">{{ footnoteNumber }}</span>
      {{ caption }}
    </figcaption>
  </figure>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  src: {
    type: String,
    required: true
  },
  caption: String,
  alt: String,
  footnoteNumber: [String, Number],

  // Size control
  size: {
    type: Number,  // Percentage of container width
    default: 80
  },
  maxWidth: String,  // e.g., '600px', '100%'

  // Alignment
  captionAlign: {
    type: String,
    default: 'center'  // 'left', 'center', 'right'
  }
})

const wrapperStyle = computed(() => ({
  maxWidth: props.maxWidth || '100%'
}))

const imageContainerStyle = computed(() => ({
  width: '100%'
}))

const imageStyle = computed(() => ({
  width: `${props.size}%`,
  height: 'auto',
  display: 'block'
}))

const captionClass = computed(() => {
  const alignmentMap = {
    left: 'text-left',
    center: 'text-center',
    right: 'text-right'
  }
  return alignmentMap[props.captionAlign] || 'text-center'
})
</script>
