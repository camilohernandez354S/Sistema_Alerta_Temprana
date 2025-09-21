<template>
  <div class="card-info">
    <h2>{{ title }}</h2>
    <p>{{ value }}</p>
  </div>
</template>

<script setup>
defineProps({
  title: String,
  value: [String, Number]
})
</script>

<style scoped>
.card-info {
  background: #222;
  color: #fff;
  border-radius: 8px;
  padding: 1rem 2rem;
  min-width: 150px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.card-info h2 {
  font-size: 1.1rem;
  margin-bottom: 0.5rem;
}
.card-info p {
  font-size: 1.5rem;
  font-weight: bold;
}
</style>
