<script setup>
import { computed, useAttrs, defineProps } from "vue";
import { useRouter } from "vue-router";

const props = defineProps();
const type = computed(() => props.type || "button");
const size = computed(() => props.size || "md");
const isActive = computed(() => props.isActive || false);

const router = useRouter();

const buttonSizeClass = computed(() => size.value);
const buttonTypeClass = computed(() => type.value);

const attrs = useAttrs();

function handleClick() {
  if (props.to) {
    router.push(props.to);
  }
}
</script>

<template>
  <button
    :class="[
      'toggle-button',
      props.class,
      buttonSizeClass,
      buttonTypeClass,
      { active: isActive },
    ]"
    v-bind="attrs"
    @click="handleClick"
  >
    <slot></slot>
  </button>
</template>

<style scoped lang="scss">
.toggle-button {
  white-space: nowrap;
  padding: 10px 20px;
  font-size: 16px;
  border: 1px solid #ccc;
  border-radius: 8px;
  background-color: white;
  color: var(--c-text);
  text-align: center;
  cursor: pointer;

  &.tag {
    background-color: #f5f5f5;
    cursor: default;
    border: none;
    font-weight: 600;
  }

  &.active {
    background-color: #000;
    color: #fff;

    &:hover {
      background-color: rgba(0, 0, 0, 0.8);
    }
  }

  &:hover {
    background-color: rgba(236, 236, 236, 0.5);
  }

  &.sm {
    padding: 4px 10px;
    font-size: 12px;
  }

  &.md {
    padding: 8px 12px;
    font-size: 14px;
  }

  &:disabled {
    pointer-events: none;
  }
}
</style>
