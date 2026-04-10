<template>
  <div class="slidev-layout pg-split h-full flex" :class="layoutClass">
    <!-- Content Panel -->
    <div class="content-panel p-4 overflow-y-auto" :style="contentStyle">
      <slot name="content" />
      <!-- Fallback to 'left' slot for backwards compatibility -->
      <slot name="left" />
    </div>

    <!-- Image Panel -->
    <div class="image-panel p-4 flex items-center justify-center" :style="imageStyle">
      <comFigure
        v-if="image"
        :src="image"
        :caption="caption"
        :footnoteNumber="footnoteNumber"
        :size="imageSize"
      />
      <!-- Allow custom content in image area -->
      <slot name="image" />
      <!-- Fallback to 'right' slot for backwards compatibility -->
      <slot name="right" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import comFigure from '../components/comFigure.vue'

const props = defineProps({
  // Image properties
  image: String,
  caption: String,
  footnoteNumber: [String, Number],
  imageSize: {
    type: Number,
    default: 85
  },

  // Layout configuration
  imagePosition: {
    type: String,
    default: 'right',  // 'left' or 'right'
    validator: (value) => ['left', 'right'].includes(value)
  },
  imageWidth: {
    type: Number,
    default: 40  // Percentage: 40% for image, 60% for content
  }
})

const layoutClass = computed(() => {
  return props.imagePosition === 'left' ? 'flex-row-reverse' : 'flex-row'
})

const contentWidth = computed(() => 100 - props.imageWidth)

const contentStyle = computed(() => ({
  flex: `0 0 ${contentWidth.value}%`
}))

const imageStyle = computed(() => ({
  flex: `0 0 ${props.imageWidth}%`
}))
</script>

<style scoped>
.pg-split {
  width: 100%;
}

/* Typography hierarchy */
.content-panel :deep(h1) {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
  color: var(--slidev-theme-primary, #3B82F6);
}

.content-panel :deep(h2) {
  font-size: 2rem;
  font-weight: 600;
  margin-bottom: 0.8rem;
  color: var(--slidev-theme-primary, #3B82F6);
}

.content-panel :deep(h3) {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 0.6rem;
  color: var(--slidev-theme-secondary, #1F2937);
}

.content-panel :deep(ul),
.content-panel :deep(ol) {
  margin: 0.5rem 0;
  padding-left: 1.5rem;
}

.content-panel :deep(li) {
  margin-bottom: 0.4rem;
  line-height: 1.6;
}

.content-panel :deep(p) {
  margin-bottom: 0.8rem;
  line-height: 1.6;
}

.content-panel :deep(blockquote) {
  border-left: 4px solid var(--slidev-theme-primary, #3B82F6);
  padding-left: 1rem;
  margin: 1rem 0;
  font-style: italic;
  color: var(--slidev-theme-secondary, #6B7280);
}
</style>
