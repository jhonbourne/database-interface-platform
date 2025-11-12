import React from 'react';
import { Menu } from 'antd';
import './MenuButton.css';

const MenuButton = ({ names = [], onClick }) => {
    let items = [];
    if (names && names.length > 0) {
        items = names.map((nam) => ({
            key: nam,
            label: (
                // Render labels as divs that can wrap so long labels are fully visible.
                <div className="menu-label">{nam}</div>
            ),
            // keep native title for hover tooltip as fallback
            title: nam
        }));
    } else {
        items = [{ key: '', label: 'No table!' }];
    }

    return (
        // wrapper gives the menu a sticky position so it stays visible while
        // the main content scrolls. top offset can be adjusted as needed.
        <div className="menu-wrapper">
            <Menu
                onClick={onClick}
                className="data-menu"
                mode="inline"
                items={items}
            />
        </div>
    );
};

export default MenuButton;