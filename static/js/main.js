/**
 * 自定义JavaScript功能
 * 遵循Google Python Style Guide注释规范
 */

/**
 * 页面加载完成后执行
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Django Ninja Web应用已加载');
    
    // 初始化所有功能
    initializeFormValidation();
    initializeAnimations();
    initializeResponsiveFeatures();
    initializeDropdowns();
    initializeNavScrollEffect();
    initializeNavActive();
    initializeAuthFeatures();
});

/**
 * 表单验证功能
 */
function initializeFormValidation() {
    // 获取所有需要验证的表单
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        });
    });
    
    // 实时验证
    const inputs = document.querySelectorAll('.form-control');
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            validateField(this);
        });
        
        input.addEventListener('input', function() {
            if (this.classList.contains('is-invalid')) {
                validateField(this);
            }
        });
    });
}

/**
 * 验证单个字段
 * @param {HTMLElement} field - 要验证的字段元素
 */
function validateField(field) {
    const formGroup = field.closest('.form-group') || field.parentElement;
    const errorMessage = formGroup.querySelector('.invalid-feedback') || formGroup.querySelector('.error-message');
    
    if (field.validity.valid) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
        if (errorMessage) {
            errorMessage.style.display = 'none';
        }
    } else {
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');
        if (errorMessage) {
            errorMessage.style.display = 'block';
            errorMessage.textContent = getValidationMessage(field);
        }
    }
}

/**
 * 获取验证错误消息
 * @param {HTMLElement} field - 字段元素
 * @returns {string} 错误消息
 */
function getValidationMessage(field) {
    if (field.validity.valueMissing) {
        return `${field.placeholder || field.name}不能为空`;
    } else if (field.validity.typeMismatch) {
        return `请输入有效的${field.type === 'email' ? '邮箱地址' : '格式'}`;
    } else if (field.validity.tooShort) {
        return `${field.placeholder || field.name}长度不能少于${field.minLength}个字符`;
    } else if (field.validity.tooLong) {
        return `${field.placeholder || field.name}长度不能超过${field.maxLength}个字符`;
    } else if (field.validity.patternMismatch) {
        return `请输入有效的格式`;
    }
    return field.validationMessage || '输入格式不正确';
}

/**
 * 初始化动画效果
 */
function initializeAnimations() {
    // 添加滚动动画
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in-up');
                    observer.unobserve(entry.target);
                }
            });
        });
        
        animatedElements.forEach(element => {
            observer.observe(element);
        });
    }
    
    // 添加加载动画
    const loader = document.querySelector('.page-loader');
    if (loader) {
        setTimeout(() => {
            loader.style.opacity = '0';
            setTimeout(() => {
                loader.style.display = 'none';
            }, 300);
        }, 500);
    }
}

/**
 * 响应式功能初始化
 */
function initializeResponsiveFeatures() {
    const appToggler = document.getElementById('appNavbarToggler');
    const appMenu = document.getElementById('appNavbar');
    if (appToggler && appMenu) {
        appToggler.addEventListener('click', function() {
            const isExpanded = this.getAttribute('aria-expanded') === 'true';
            this.setAttribute('aria-expanded', (!isExpanded).toString());
            appMenu.classList.toggle('is-open');
        });
        const appLinks = appMenu.querySelectorAll('.app-navbar__link');
        appLinks.forEach(link => {
            link.addEventListener('click', () => {
                if (window.innerWidth < 992) {
                    appMenu.classList.remove('is-open');
                    appToggler.setAttribute('aria-expanded', 'false');
                }
            });
        });
    }
    
    // 响应式表格
    const tables = document.querySelectorAll('.table-responsive');
    tables.forEach(table => {
        table.addEventListener('scroll', function() {
            this.classList.add('table-scrolling');
            const self = this;
            if (self.scrollTimeout) {
                clearTimeout(self.scrollTimeout);
            }
            self.scrollTimeout = setTimeout(() => {
                self.classList.remove('table-scrolling');
                self.scrollTimeout = null;
            }, 1000);
        });
    });
}

function initializeDropdowns() {
    const toggle = document.getElementById('userDropdownToggle');
    if (toggle) {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            const menu = this.nextElementSibling;
            if (menu && menu.classList.contains('app-dropdown__menu')) {
                const isShown = menu.classList.contains('is-open');
                document.querySelectorAll('.app-dropdown__menu.is-open').forEach(m => m.classList.remove('is-open'));
                if (!isShown) {
                    menu.classList.add('is-open');
                    this.setAttribute('aria-expanded', 'true');
                } else {
                    this.setAttribute('aria-expanded', 'false');
                }
            }
        });
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.app-dropdown')) {
                document.querySelectorAll('.app-dropdown__menu.is-open').forEach(m => m.classList.remove('is-open'));
                toggle.setAttribute('aria-expanded', 'false');
            }
        });
    }
}

function initializeNavScrollEffect() {
    const nav = document.querySelector('.app-navbar');
    if (!nav) return;
    const apply = () => {
        if (window.scrollY > 2) {
            nav.classList.add('app-navbar--scrolled');
        } else {
            nav.classList.remove('app-navbar--scrolled');
        }
    };
    apply();
    window.addEventListener('scroll', apply, { passive: true });
}

function initializeNavActive() {
    const links = Array.from(document.querySelectorAll('.app-navbar__links .app-navbar__link'));
    if (!links.length) return;
    const headerHeight = 56;
    const linkById = {};
    links.forEach(link => {
        const href = link.getAttribute('href') || '';
        const idx = href.indexOf('#');
        if (idx !== -1) {
            const id = href.slice(idx + 1);
            if (id) linkById[id] = link;
        }
        link.addEventListener('click', () => setActive(link));
    });
    function setActive(activeLink) {
        links.forEach(l => {
            const is = l === activeLink;
            l.classList.toggle('is-active', is);
            if (is) {
                l.setAttribute('aria-current', 'page');
            } else {
                l.removeAttribute('aria-current');
            }
        });
    }
    const hashInit = window.location.hash.replace('#', '');
    if (hashInit && linkById[hashInit]) setActive(linkById[hashInit]);
    const sections = Object.keys(linkById).map(id => document.getElementById(id)).filter(Boolean);
    if ('IntersectionObserver' in window && sections.length) {
        const observer = new IntersectionObserver(entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const id = entry.target.id;
                    const link = linkById[id];
                    if (link) setActive(link);
                }
            });
        }, { rootMargin: `-${headerHeight}px 0px -70% 0px`, threshold: 0.25 });
        sections.forEach(sec => observer.observe(sec));
    }
    window.addEventListener('hashchange', () => {
        const h = window.location.hash.replace('#', '');
        const link = linkById[h];
        if (link) setActive(link);
    });
}

/**
 * 认证功能初始化
 */
function initializeAuthFeatures() {
    // 密码可见性切换
    const passwordToggleButtons = document.querySelectorAll('.password-toggle');
    
    passwordToggleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            const passwordField = document.querySelector(targetId);
            
            if (passwordField) {
                const type = passwordField.getAttribute('type') === 'password' ? 'text' : 'password';
                passwordField.setAttribute('type', type);
                
                // 更新图标
                const icon = this.querySelector('i') || this;
                if (type === 'password') {
                    icon.classList.remove('bi-eye-slash');
                    icon.classList.add('bi-eye');
                } else {
                    icon.classList.remove('bi-eye');
                    icon.classList.add('bi-eye-slash');
                }
            }
        });
    });
    
    // 记住我功能
    const rememberMeCheckbox = document.querySelector('#rememberMe');
    if (rememberMeCheckbox) {
        // 从localStorage恢复状态
        const remembered = localStorage.getItem('rememberMe') === 'true';
        rememberMeCheckbox.checked = remembered;
        
        rememberMeCheckbox.addEventListener('change', function() {
            localStorage.setItem('rememberMe', this.checked);
        });
    }
    
    // 自动登录功能（如果记住我被选中）
    const loginForm = document.querySelector('#loginForm');
    if (loginForm && localStorage.getItem('rememberMe') === 'true') {
        const username = localStorage.getItem('rememberedUsername');
        if (username) {
            const usernameField = loginForm.querySelector('#username');
            if (usernameField) {
                usernameField.value = username;
            }
        }
    }
}

/**
 * 显示加载状态
 * @param {HTMLElement} element - 要显示加载状态的元素
 * @param {boolean} show - 是否显示加载状态
 */
function setLoadingState(element, show = true) {
    if (show) {
        element.classList.add('loading');
        element.disabled = true;
        
        // 添加加载图标
        const originalContent = element.innerHTML;
        element.setAttribute('data-original-content', originalContent);
        element.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>处理中...';
    } else {
        element.classList.remove('loading');
        element.disabled = false;
        
        // 恢复原始内容
        const originalContent = element.getAttribute('data-original-content');
        if (originalContent) {
            element.innerHTML = originalContent;
        }
    }
}

/**
 * 显示通知消息
 * @param {string} message - 消息内容
 * @param {string} type - 消息类型 (success, error, warning, info)
 * @param {number} duration - 显示时长（毫秒）
 */
function showNotification(message, type = 'info', duration = 3000) {
    const notificationContainer = document.getElementById('notificationContainer') || createNotificationContainer();
    
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show notification`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    notificationContainer.appendChild(notification);
    
    // 自动移除
    setTimeout(() => {
        if (notification.parentNode) {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 150);
        }
    }, duration);
}

/**
 * 创建通知容器
 * @returns {HTMLElement} 通知容器元素
 */
function createNotificationContainer() {
    const container = document.createElement('div');
    container.id = 'notificationContainer';
    container.className = 'notification-container';
    container.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1050;
        max-width: 300px;
    `;
    document.body.appendChild(container);
    return container;
}

/**
 * AJAX请求封装
 * @param {string} url - 请求URL
 * @param {Object} options - 请求选项
 * @returns {Promise} Promise对象
 */
async function makeRequest(url, options = {}) {
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken') || '',
            'X-Requested-With': 'XMLHttpRequest'
        },
        credentials: 'same-origin'
    };
    
    const mergedOptions = { ...defaultOptions, ...options };
    
    if (mergedOptions.body && typeof mergedOptions.body === 'object') {
        mergedOptions.body = JSON.stringify(mergedOptions.body);
    }
    
    try {
        const response = await fetch(url, mergedOptions);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return await response.json();
        } else {
            return await response.text();
        }
    } catch (error) {
        console.error('请求失败:', error);
        showNotification(`请求失败: ${error.message}`, 'error');
        throw error;
    }
}

/**
 * 获取Cookie值
 * @param {string} name - Cookie名称
 * @returns {string|null} Cookie值
 */
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) {
        return parts.pop().split(';').shift();
    }
    return null;
}

/**
 * 防抖函数
 * @param {Function} func - 要执行的函数
 * @param {number} wait - 等待时间（毫秒）
 * @returns {Function} 防抖后的函数
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * 节流函数
 * @param {Function} func - 要执行的函数
 * @param {number} limit - 时间限制（毫秒）
 * @returns {Function} 节流后的函数
 */
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}
