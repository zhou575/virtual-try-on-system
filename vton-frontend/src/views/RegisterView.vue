<template>
    <div class="register-container">
        <el-card class="register-card">
            <h2>用户注册</h2>
            <el-form :model="registerForm" :rules="registerRules" ref="registerFormRef" label-width="80px">
                <el-form-item label="账号" prop="account">
                    <el-input v-model="registerForm.account" placeholder="请输入邮箱或手机号" />
                </el-form-item>
                <el-form-item label="验证码" prop="code">
                    <el-input v-model="registerForm.code" placeholder="请输入验证码" style="width: 69%" />
                    <el-button type="primary" @click="sendVerifyCode" :disabled="countdown > 0">
                        {{ countdown > 0 ? `${countdown}秒后重新发送` : '发送验证码' }}
                    </el-button>
                </el-form-item>
                <el-form-item label="密码" prop="password">
                    <el-input v-model="registerForm.password" type="password" placeholder="请输入密码" />
                </el-form-item>
                <el-form-item label="确认密码" prop="confirmPassword">
                    <el-input v-model="registerForm.confirmPassword" type="password" placeholder="请再次输入密码" />
                </el-form-item>
                <el-form-item>
                    <el-button type="primary" @click="handleRegister" :loading="registerLoading"
                        style="width: 100%">注册</el-button>
                </el-form-item>
                <el-form-item>
                    <p class="login-link">已有账号？<a href="/login">立即登录</a></p>
                </el-form-item>
            </el-form>
        </el-card>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElLoading } from 'element-plus';
import { usersAPI } from '../api';

const router = useRouter();

// 注册表单
const registerForm = reactive({
    account: '',
    code: '',
    password: '',
    confirmPassword: ''
});

// 表单验证规则
const registerRules = reactive({
    account: [
        { required: true, message: '请输入账号', trigger: 'blur' },
        {
            validator: (rule: any, value: string, callback: any) => {
                // 验证邮箱或手机号格式
                const emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;
                const phoneRegex = /^1[3-9]\d{9}$/;
                if (!emailRegex.test(value) && !phoneRegex.test(value)) {
                    callback(new Error('请输入有效的邮箱或手机号'));
                } else {
                    callback();
                }
            },
            trigger: 'blur'
        }
    ],
    code: [
        { required: true, message: '请输入验证码', trigger: 'blur' }
    ],
    password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
    ],
    confirmPassword: [
        { required: true, message: '请再次输入密码', trigger: 'blur' },
        {
            validator: (rule: any, value: string, callback: any) => {
                if (value !== registerForm.password) {
                    callback(new Error('两次输入密码不一致'));
                } else {
                    callback();
                }
            },
            trigger: 'blur'
        }
    ]
});

// 表单引用
const registerFormRef = ref();

// 加载状态
const registerLoading = ref(false);

// 倒计时
const countdown = ref(0);

// 发送验证码
const sendVerifyCode = () => {
    // 验证账号格式
    const emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;
    const phoneRegex = /^1[3-9]\d{9}$/;

    if (!emailRegex.test(registerForm.account) && !phoneRegex.test(registerForm.account)) {
        ElMessage.error('请输入有效的邮箱或手机号');
        return;
    }

    // 发送验证码
    usersAPI.sendVerificationCode(
        {
            account: registerForm.account
        }
    ).then((data) => {
        ElMessage.success(data.message);
    }).catch((data) => {
        ElMessage.error(data.detail);
    });

    // 开始倒计时
    countdown.value = 60;
    const timer = setInterval(() => {
        countdown.value--;
        if (countdown.value <= 0) {
            clearInterval(timer);
        }
    }, 1000);
};

// 注册
const handleRegister = () => {
    if (!registerFormRef.value) return;

    registerFormRef.value.validate((valid: boolean) => {
        if (valid) {
            const loading = ElLoading.service({
                lock: true,
                text: '正在注册...',
                background: 'rgba(0, 0, 0, 0.7)'
            });

            usersAPI.registerUser(
                {
                    account: registerForm.account,
                    code: registerForm.code,
                    password: registerForm.password,
                    password_confirm: registerForm.confirmPassword
                }
            ).then(() => {
                ElMessage.success('注册成功！');
                router.push('/login');
            }).catch(() => {
                ElMessage.error('注册失败，请稍后重试');
            }).finally(() => {
                loading.close();
            });
        } else {
            ElMessage.error('请检查表单是否填写正确');
        }
    });
};
</script>

<style scoped>
.register-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: calc(100vh - 60px);
    background-color: #f5f7fa;
}

.register-card {
    width: 500px;
    padding: 20px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.register-card h2 {
    text-align: center;
    margin-bottom: 20px;
    color: #303133;
}

.login-link {
    text-align: center;
    margin: 0;
}

.login-link a {
    color: #409eff;
    text-decoration: none;
}

.login-link a:hover {
    text-decoration: underline;
}
</style>