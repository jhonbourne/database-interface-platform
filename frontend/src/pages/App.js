import './App.css';
import Naviagtor from '../components/TablePanel/Navigator'
import UserMenu from '../components/UserMenu/UserMenu';
import GetInfo from '../components/GetInfo/GetInfo';
import useFetchLogger from '../hooks/useFetchLogger';

import { Layout } from 'antd';
const { Header, Footer, Sider, Content } = Layout;

function App() {
  useFetchLogger('App');
  return (
    <Layout>
      <Header className="app-header">
        <span className="app-header-title">Data Panel</span>
        <UserMenu />
      </Header>
      <Naviagtor />
    </Layout>
  );
}

export default App;
