import { useState, useEffect } from "react";
import {URLS} from '../urls';
import MenuButton from "./MenuButton";
import DataBoard from "./DataBoard";

import { Layout, theme } from 'antd';
const { Sider, Content } = Layout;

function Navigator(props){
    // Set states
    const [menures, setMenures] = useState({data: []});
    const [onshow, setOnshow] = useState('');
    const [tableres, setTableres] = useState({});

    // When load the page, get the names of tables for showing
    useEffect(() => {
        // url for showing tables
        const url = URLS['TablePanel'];

        // Redirect
        // window.location.href = url
        // Get table names
        fetch(url)
            .then(response => {//alert(response.status);
                return (response.json()) })
            .then(dat => {setMenures(dat); })
            .catch(error => {console.error("Request error",error)});        
    }, [])


    // Change the table on show if any button on the menu is clicked
    function onSelectMenu(e) {
        setOnshow(e.key);
    }

    // Show table contents if any change
    useEffect(() => {
        if (onshow.length > 0) {
            // url for showing table
            const url = URLS['TablePanel'];
            const query_url = `${url}/${onshow}`;

            // Request table data
            fetch(query_url)
                .then(response => response.json())
                .then(dat => { setTableres(dat); })
                .catch(error => {console.error("Request error",error)});
        } else {
            setTableres({ success: false, status: "No table available."});
        }
        
    }, [onshow])

    // items are provided by MenuButton child; keep menures.data as source

    const {
        token: { colorBgContainer, borderRadiusLG },
    } = theme.useToken();
    return (
        <Layout>
            <Sider>
                <MenuButton
                    onClick={onSelectMenu}
                    names={menures.data}
                />
            </Sider>
            <Layout>                    
                <Content
                    style={{
                        margin: '24px 16px',
                        padding: 16,
                        minHeight: 600,
                        background: colorBgContainer,
                        borderRadius: borderRadiusLG
                    }}
                >
                    <DataBoard
                        info={tableres}
                        rowHeight={48}
                    />
                </Content>            
            </Layout>
        </Layout>
    )
}

export default Navigator;