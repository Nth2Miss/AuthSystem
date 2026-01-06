<template>
  <form @submit.prevent="handleSubmit" class="login-form">
    <h2>用户登录</h2>
    
    <div class="form-group">
      <label for="email">邮箱地址</label>
      <input 
        type="email" 
        id="email" 
        v-model="form.email" 
        placeholder="请输入邮箱地址"
        required
      />
    </div>
    
    <div class="form-group">
      <label for="password">密码</label>
      <input 
        type="password" 
        id="password" 
        v-model="form.password" 
        placeholder="请输入密码"
        required
      />
    </div>
    
    <div class="form-group">
      <label for="login-code">图形验证码</label>
      <div class="captcha-group">
        <input 
          type="text" 
          id="login-code" 
          v-model="form.code" 
          placeholder="请输入验证码"
          maxlength="4"
          required
        />
        <div class="captcha-image-container">
          <img 
            v-if="captchaImage" 
            :src="captchaImage" 
            alt="验证码" 
            @click="refreshCaptcha"
            class="captcha-image"
          />
          <button 
            type="button" 
            @click="refreshCaptcha" 
            class="refresh-btn"
          >
            刷新
          </button>
        </div>
      </div>
    </div>
    
    <button 
      type="submit" 
      class="submit-btn" 
      :disabled="submitting"
    >
      {{ submitting ? '登录中...' : '登录' }}
    </button>
    
    <div v-if="message" class="message" :class="messageType">
      {{ message }}
    </div>
    
    <p class="switch-link">
      没有账号？<a href="#" @click.prevent="$emit('switch-to-register')">立即注册</a>
    </p>
  </form>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Login',
  emits: ['switch-to-register'],
  data() {
    return {
      form: {
        email: '',
        password: '',
        code: ''
      },
      submitting: false,
      message: '',
      messageType: '',
      captchaImage: '',
      captchaKey: ''
    }
  },
  mounted() {
    this.loadCaptcha();
  },
  methods: {
    async loadCaptcha() {
      try {
        const response = await axios.get('/api/generate-captcha');
        this.captchaImage = response.data.image;
        this.captchaKey = response.data.captcha_key;
      } catch (error) {
        this.showMessage(
          error.response?.data?.error || '验证码加载失败，请稍后重试', 
          'error'
        )
      }
    },
    
    async refreshCaptcha() {
      try {
        const response = await axios.post('/api/refresh-captcha');
        this.captchaImage = response.data.image;
        this.captchaKey = response.data.captcha_key;
      } catch (error) {
        this.showMessage(
          error.response?.data?.error || '验证码刷新失败，请稍后重试', 
          'error'
        )
      }
    },
    
    async handleSubmit() {
      if (!this.form.email || !this.form.password || !this.form.code) {
        this.showMessage('请填写所有字段', 'error')
        return
      }
      
      if (!this.captchaKey) {
        this.showMessage('请先加载图形验证码', 'error')
        return
      }
      
      if (!this.isValidEmail(this.form.email)) {
        this.showMessage('邮箱格式不正确', 'error')
        return
      }
      
      if (this.form.code.length !== 4 || !/^\d{4}$/.test(this.form.code)) {
        this.showMessage('请输入4位数字验证码', 'error')
        return
      }
      
      this.submitting = true
      
      try {
        const loginData = {
          email: this.form.email,
          password: this.form.password,
          code: this.form.code,
          captcha_key: this.captchaKey
        };
        
        const response = await axios.post('/api/login', loginData)
        this.showMessage(response.data.message, 'success')
        
        // 登录成功后清空表单
        this.form = {
          email: '',
          password: '',
          code: ''
        }
        
        // 实际应用中可以将用户信息保存到本地存储或状态管理中
        console.log('登录成功', response.data.user)
      } catch (error) {
        this.showMessage(
          error.response?.data?.error || '登录失败，请稍后重试', 
          'error'
        )
      } finally {
        this.submitting = false
      }
    },
    
    isValidEmail(email) {
      const pattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
      return pattern.test(email)
    },
    
    startCountdown() {
      this.countdown = 60
      const timer = setInterval(() => {
        this.countdown--
        if (this.countdown <= 0) {
          clearInterval(timer)
        }
      }, 1000)
    },
    
    showMessage(text, type) {
      this.message = text
      this.messageType = type
      setTimeout(() => {
        this.message = ''
      }, 5000)
    }
  }
}
</script>

<style scoped>
.login-form {
  width: 100%;
}

h2 {
  text-align: center;
  margin-bottom: 20px;
  color: #333;
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 5px;
  color: #555;
  font-weight: 500;
}

input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  transition: border-color 0.3s;
}

input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.captcha-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.captcha-image-container {
  display: flex;
  align-items: center;
  gap: 10px;
}

.captcha-image {
  height: 40px;
  cursor: pointer;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.refresh-btn {
  padding: 10px 15px;
  background-color: #6c757d;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.refresh-btn:hover:not(:disabled) {
  background-color: #5a6268;
}

.refresh-btn:disabled {
  background-color: #adb5bd;
  cursor: not-allowed;
}

.submit-btn {
  width: 100%;
  padding: 12px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.submit-btn:hover:not(:disabled) {
  background-color: #0056b3;
}

.submit-btn:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

.message {
  margin-top: 15px;
  padding: 10px;
  border-radius: 4px;
  text-align: center;
}

.message.success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.message.error {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.switch-link {
  text-align: center;
  margin-top: 15px;
  color: #666;
}

.switch-link a {
  color: #007bff;
  text-decoration: none;
}

.switch-link a:hover {
  text-decoration: underline;
}
</style>