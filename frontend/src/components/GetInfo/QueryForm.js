
function QueryForm(props) {
    return (
        <form action={props.onQuerySubmit}>
            <input type="text" name={props.queryName} />
            <button type='submit'>Get information</button>
        </form>
    );
}

export default QueryForm