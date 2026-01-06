<template>
  <div id="app">
    <div class="container">
      <h1>用户认证系统</h1>
      <div class="auth-container">
        <div class="auth-tabs">
          <button 
            :class="['tab', { active: activeTab === 'register' }]" 
            @click="activeTab = 'register'"
          >
            注册
          </button>
          <button 
            :class="['tab', { active: activeTab === 'login' }]" 
            @click="activeTab = 'login'"
          >
            登录
          </button>
        </div>
        
        <div class="auth-content">
          <Register v-if="activeTab === 'register'" @switch-to-login="activeTab = 'login'" />
          <Login v-if="activeTab === 'login'" @switch-to-register="activeTab = 'register'" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Register from './components/Register.vue'
import Login from './components/Login.vue'

export default {
  name: 'App',
  components: {
    Register,
    Login
  },
  data() {
    return {
      activeTab: 'register'
    }
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Arial', sans-serif;
  background-color: #f5f5f5;
}

#app {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.container {
  width: 100%;
  max-width: 500px;
  padding: 20px;
}

h1 {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
}

.auth-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.auth-tabs {
  display: flex;
  border-bottom: 1px solid #eee;
}

.tab {
  flex: 1;
  padding: 15px;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.3s;
}

.tab.active {
  background-color: #007bff;
  color: white;
}

.tab:not(.active):hover {
  background-color: #f0f0f0;
}

.auth-content {
  padding: 30px;
}
</style>