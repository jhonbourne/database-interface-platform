import { redirectLoginCode } from '../router/index';

// Pure helper: return a redirect path when login is required, otherwise null.
export default function shouldLogin(status) {
    if (status === redirectLoginCode) {
        return '/user/login';
    }
    return null;
}