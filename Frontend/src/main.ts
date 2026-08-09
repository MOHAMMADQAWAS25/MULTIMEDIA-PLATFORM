import './styles.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8001/api/v1';

type ApiError = {
  error?: {
    code?: string;
    message?: string;
  };
  detail?: unknown;
};

type SignupStarted = {
  email: string;
  expires_at: string;
  message: string;
};

type UserRead = {
  id: string;
  full_name: string;
  email: string;
  department: string | null;
  major: string | null;
  role: string;
  is_active: boolean;
  is_verified: boolean;
};

type AuthToken = {
  access_token: string;
  token_type: string;
  expires_at: string;
  user: UserRead;
};

const app = document.querySelector<HTMLMainElement>('#app');

if (app === null) {
  throw new Error('App root was not found.');
}

let authToken = localStorage.getItem('inkfig_access_token') ?? '';
let signupEmail = '';

app.innerHTML = `
  <section class="shell">
    <aside class="brand-panel">
      <div class="brand-mark">IF</div>
      <div>
        <p class="eyebrow">Hebron University</p>
        <h1>InkFig</h1>
        <p class="lead">Create your university art profile, verify your email, and enter the platform securely.</p>
      </div>
      <div class="status-card">
        <span class="status-dot"></span>
        <span>Backend: <strong id="api-status">checking</strong></span>
      </div>
    </aside>

    <section class="auth-panel">
      <div class="tabs" role="tablist" aria-label="Authentication views">
        <button class="tab active" data-tab="signup" type="button">Sign Up</button>
        <button class="tab" data-tab="verify" type="button">Verify Code</button>
        <button class="tab" data-tab="login" type="button">Login</button>
        <button class="tab" data-tab="profile" type="button">Me</button>
      </div>

      <form class="view active" id="signup-view">
        <div class="form-heading">
          <h2>Create account</h2>
          <p>Use a Hebron University email address.</p>
        </div>
        <label>Full name<input name="full_name" autocomplete="name" required minlength="2" maxlength="120" /></label>
        <label>Email<input name="email" type="email" autocomplete="email" required placeholder="202012345@students.hebron.edu" /></label>
        <div class="grid-2">
          <label>Department<input name="department" maxlength="120" placeholder="Information Technology" /></label>
          <label>Major<input name="major" maxlength="120" placeholder="Software Engineering" /></label>
        </div>
        <div class="grid-2">
          <label>Password<input name="password" type="password" autocomplete="new-password" required minlength="8" /></label>
          <label>Confirm password<input name="confirm_password" type="password" autocomplete="new-password" required minlength="8" /></label>
        </div>
        <div class="rule-box">
          <span>Allowed emails:</span>
          <code>[studentnumber]@students.hebron.edu</code>
          <code>[name]@hebron.edu</code>
        </div>
        <button class="primary" type="submit">Send verification code</button>
      </form>

      <form class="view" id="verify-view">
        <div class="form-heading">
          <h2>Verify email</h2>
          <p>Enter the 6-digit code sent to your inbox.</p>
        </div>
        <label>Email<input name="email" type="email" autocomplete="email" required /></label>
        <label>Code<input name="code" inputmode="numeric" pattern="\\d{6}" maxlength="6" required placeholder="123456" /></label>
        <button class="primary" type="submit">Create account</button>
      </form>

      <form class="view" id="login-view">
        <div class="form-heading">
          <h2>Login</h2>
          <p>Use your verified InkFig account.</p>
        </div>
        <label>Email<input name="email" type="email" autocomplete="email" required /></label>
        <label>Password<input name="password" type="password" autocomplete="current-password" required /></label>
        <button class="primary" type="submit">Login</button>
      </form>

      <section class="view" id="profile-view">
        <div class="form-heading">
          <h2>Current user</h2>
          <p>Your JWT-protected account information.</p>
        </div>
        <div class="profile-box" id="profile-output">No user loaded.</div>
        <div class="button-row">
          <button class="primary" id="load-me" type="button">Load profile</button>
          <button class="secondary" id="logout" type="button">Logout</button>
        </div>
      </section>

      <section class="message" id="message" aria-live="polite"></section>
    </section>
  </section>
`;

const message = document.querySelector<HTMLElement>('#message')!;
const apiStatus = document.querySelector<HTMLElement>('#api-status')!;

function setMessage(text: string, kind: 'success' | 'error' | 'info' = 'info'): void {
  message.textContent = text;
  message.className = `message ${kind}`;
}

function switchTab(tabName: string): void {
  document.querySelectorAll<HTMLButtonElement>('.tab').forEach((tab) => {
    tab.classList.toggle('active', tab.dataset.tab === tabName);
  });
  document.querySelectorAll<HTMLElement>('.view').forEach((view) => {
    view.classList.toggle('active', view.id === `${tabName}-view`);
  });
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set('Content-Type', 'application/json');
  if (authToken) {
    headers.set('Authorization', `Bearer ${authToken}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });
  const payload = (await response.json().catch(() => ({}))) as T | ApiError;

  if (!response.ok) {
    const errorPayload = payload as ApiError;
    const text =
      errorPayload.error?.message ??
      (typeof errorPayload.detail === 'string' ? errorPayload.detail : 'Request failed.');
    throw new Error(text);
  }

  return payload as T;
}

function getFormData(form: HTMLFormElement): Record<string, string> {
  return Object.fromEntries(new FormData(form).entries()) as Record<string, string>;
}

document.querySelectorAll<HTMLButtonElement>('.tab').forEach((tab) => {
  tab.addEventListener('click', () => switchTab(tab.dataset.tab ?? 'signup'));
});

document.querySelector<HTMLFormElement>('#signup-view')!.addEventListener('submit', async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const data = getFormData(form);

  try {
    const result = await request<SignupStarted>('/auth/signup', {
      method: 'POST',
      body: JSON.stringify({
        full_name: data.full_name,
        email: data.email,
        department: data.department || null,
        major: data.major || null,
        password: data.password,
        confirm_password: data.confirm_password,
      }),
    });
    signupEmail = result.email;
    const verifyEmail = document.querySelector<HTMLInputElement>('#verify-view input[name="email"]')!;
    verifyEmail.value = signupEmail;
    switchTab('verify');
    setMessage(`Code sent to ${result.email}. It expires at ${new Date(result.expires_at).toLocaleTimeString()}.`, 'success');
  } catch (error) {
    setMessage(error instanceof Error ? error.message : 'Signup failed.', 'error');
  }
});

document.querySelector<HTMLFormElement>('#verify-view')!.addEventListener('submit', async (event) => {
  event.preventDefault();
  const data = getFormData(event.currentTarget);

  try {
    const user = await request<UserRead>('/auth/signup/verify', {
      method: 'POST',
      body: JSON.stringify({
        email: data.email,
        code: data.code,
      }),
    });
    switchTab('login');
    setMessage(`Account created for ${user.email}. You can login now.`, 'success');
  } catch (error) {
    setMessage(error instanceof Error ? error.message : 'Verification failed.', 'error');
  }
});

document.querySelector<HTMLFormElement>('#login-view')!.addEventListener('submit', async (event) => {
  event.preventDefault();
  const data = getFormData(event.currentTarget);

  try {
    const result = await request<AuthToken>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({
        email: data.email,
        password: data.password,
      }),
    });
    authToken = result.access_token;
    localStorage.setItem('inkfig_access_token', authToken);
    renderUser(result.user);
    switchTab('profile');
    setMessage(`Logged in as ${result.user.email}.`, 'success');
  } catch (error) {
    setMessage(error instanceof Error ? error.message : 'Login failed.', 'error');
  }
});

document.querySelector<HTMLButtonElement>('#load-me')!.addEventListener('click', async () => {
  try {
    const user = await request<UserRead>('/auth/me');
    renderUser(user);
    setMessage('Profile loaded.', 'success');
  } catch (error) {
    setMessage(error instanceof Error ? error.message : 'Could not load profile.', 'error');
  }
});

document.querySelector<HTMLButtonElement>('#logout')!.addEventListener('click', () => {
  authToken = '';
  localStorage.removeItem('inkfig_access_token');
  renderProfileText('No user loaded.');
  switchTab('login');
  setMessage('Logged out.', 'info');
});

function renderUser(user: UserRead): void {
  renderProfileText(`
    <dl>
      <div><dt>Name</dt><dd>${escapeHtml(user.full_name)}</dd></div>
      <div><dt>Email</dt><dd>${escapeHtml(user.email)}</dd></div>
      <div><dt>Department</dt><dd>${escapeHtml(user.department ?? 'Not set')}</dd></div>
      <div><dt>Major</dt><dd>${escapeHtml(user.major ?? 'Not set')}</dd></div>
      <div><dt>Role</dt><dd>${escapeHtml(user.role)}</dd></div>
      <div><dt>Status</dt><dd>${user.is_active ? 'Active' : 'Inactive'}</dd></div>
    </dl>
  `);
}

function renderProfileText(html: string): void {
  document.querySelector<HTMLElement>('#profile-output')!.innerHTML = html;
}

function escapeHtml(value: string): string {
  return value.replace(/[&<>"']/g, (character) => {
    const entities: Record<string, string> = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#39;',
    };
    return entities[character];
  });
}

async function checkApi(): Promise<void> {
  try {
    await request<{ status: string }>('/health');
    apiStatus.textContent = 'online';
    apiStatus.parentElement?.classList.add('online');
  } catch {
    apiStatus.textContent = 'offline';
    apiStatus.parentElement?.classList.remove('online');
  }
}

void checkApi();
