import { Dropdown, Button } from "antd";
import Logout from './Logout';
import { DownOutlined } from '@ant-design/icons';

export default function UserMenu() {
	const items = [
		{
			key: 'logout',
			label: <Logout />,
		},
	];

	return (
		<Dropdown menu={{ items }} placement="bottomRight">
            <Button>User Options</Button>
			{/* <a onClick={e => e.preventDefault()}>
				User Options <DownOutlined />
			</a> */}
		</Dropdown>
	);
}
