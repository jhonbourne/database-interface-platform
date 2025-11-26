import React, { useState, useEffect } from 'react';
import InfoForm from './InfoForm';
import InfoBoard from './InfoBoard';
import {URLS} from '../../utils/request_urls';
import { requestSettings } from '../../utils/request_settings';

function PostInfo (props) {
    // Set states
    const [post, setPost] = useState({
        body: "{}"
        ,param: ""
    });
    const [result, setResult] = useState({
        body: ""
        ,param: ""
    });
    // Set attribute name
    const childBodyName = "body";
    const childParamName = "param";

    // Monitor query request
    useEffect(() => {
        // Request url
        const url = URLS['PostInfo'];

        const settings = { ...requestSettings, method: 'POST',
             body: JSON.stringify(eval("("+post.body+")")) };
        fetch(url+'?'+post.param, settings)
            .then(response => response.json())
            .then( data => {
                setResult({
                    param: data.param
                    ,body: JSON.stringify(data.body)
                });
            }
                )
            .catch(error => {console.error("Request error: ",error)})
        // setResult({
        //     body: post.body
        //     ,param: post.param
    },[post]);

    function updatePost(formData) {
        let bodyValue = formData.get(childBodyName);
        const paramValue = formData.get(childParamName);
        // dealing invalid input of "body"
        let s = null;
        try {
            s = JSON.stringify(eval("("+bodyValue+")"))
        } catch (e) {
            alert('Input error: '+e);
            bodyValue = '{}';
        }
        setPost({body: bodyValue, param: paramValue})
    }

    return (
        <div>
            <InfoForm 
                bodyName={childBodyName} 
                paramName={childParamName}
                onQuerySubmit={updatePost} />
            <InfoBoard
                resultBodyValue={result.body}
                resultParamValue={result.param} />
        </div>
    )

}

export default PostInfo