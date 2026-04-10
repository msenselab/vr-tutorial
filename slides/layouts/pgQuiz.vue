<template>
  <div class="slidev-layout pg-quiz h-full flex flex-col">
    <!-- Title -->
    <h1 class="mb-8">
      <slot name="title">Quick Quiz</slot>
    </h1>

    <!-- Question Box -->
    <div class="flex-1 p-6 bg-blue-50 rounded-lg shadow-md">
      <p class="text-lg font-semibold mb-4">
        <slot name="question" />
      </p>

      <div class="text-base space-y-2">
        <slot name="options" />
      </div>
    </div>

    <!-- Answer Section (revealed on click) -->
    <v-click>
      <div class="mt-6 p-4 bg-green-100 rounded-lg">
        <strong class="text-lg">
          Answer: <slot name="answer-letter" />
        </strong>
        <p class="text-sm mt-2">
          <slot name="explanation" />
        </p>
      </div>
    </v-click>
  </div>
</template>

<script setup>
// No props needed for this simple layout
</script>

<style scoped>
.pg-quiz :deep(ul) {
  list-style: none;
  padding-left: 0;
}

.pg-quiz :deep(li) {
  padding: 0.5rem;
  margin-bottom: 0.5rem;
  border-radius: 0.375rem;
  transition: background-color 0.2s;
}

.pg-quiz :deep(li:hover) {
  background-color: rgba(59, 130, 246, 0.1);
}

.pg-quiz :deep(strong) {
  font-weight: 600;
}
</style>
