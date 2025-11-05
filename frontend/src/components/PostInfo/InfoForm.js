function InfoForm(props) {
    const bodyPrompt = 'Input JavaScript object using "{", "}" and ":"'
    const showSize = bodyPrompt.length
    return (
        <form action={props.onQuerySubmit}>
            body: <input type="text" name={props.bodyName} 
                placeholder={bodyPrompt} size={showSize} />
            <br />
            param: <input type="text" name={props.paramName}
                size={showSize} />
            <br />
            <button type='submit'>Get body and params</button>
        </form>
    );
}

export default InfoForm