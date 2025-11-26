import { useNavigate } from 'react-router-dom';
import { message } from 'antd';
import { URLS } from '../../utils/request_urls';
import { requestSettings } from '../../utils/request_settings';

function Logout() {
    const navigate = useNavigate();
    const logoutUrl = URLS['Logout'];

    const handleLogout = (e) => {
        if (e && e.preventDefault) e.preventDefault();
            fetch(logoutUrl, requestSettings)
            .then(async response => {
                if (!response.ok) {
                    const msg = await response.json();
                    throw new Error(msg.status);
                }
            })
            .then(message.success('Logged out'))
            // Redirect to start page after logout
            .then(navigate('/start'))
            .catch( (err) => {
            const text = err && (err.message || (err.body && JSON.stringify(err.body))) || 'Logout failed';
            message.error(text);
        } )
    };

    return (
        <a onClick={handleLogout} role="button">
            Logout
        </a>
    );
}

export default Logout;

