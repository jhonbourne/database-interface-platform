import React, { useState, useEffect } from 'react';
import QueryForm from './QueryForm';
import ResultBoard from './ResultBoard';
import {URLS} from '../../utils/request_urls';
import { requestSettings } from '../../utils/request_settings';

function GetInfo (props) {
    // Set states
    const [query, setQuery] = useState("?");
    const [result, setResult] = useState("");
    // Set attribute name
    const childQueryName = "query";

    // Monitor query request
    useEffect(() => {
        // Request url
        const url = URLS['GetInfo'];

        fetch(url+'?'+query, requestSettings)
            .then(response => response.json())
            .then(data => setResult(data.result))
        // setResult("Return "+ query);
    },[query]);

    function updateQuery(formData) {
        const get_query = formData.get(childQueryName);
        setQuery(get_query);
    }

    return (
        <div>
            <QueryForm 
                queryName={childQueryName} 
                onQuerySubmit={updateQuery} />
            <ResultBoard
                resultValue={result} />
        </div>
    )

}

export default GetInfo
