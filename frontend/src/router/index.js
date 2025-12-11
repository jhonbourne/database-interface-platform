import { createBrowserRouter, Navigate } from "react-router-dom";
import StartPage from "../pages/StartPage";
import App from "../pages/App";
import Register from "../pages/Register";
import Login from "../pages/Login";
import ImageProcesser from "../pages/ImageProcesser";

const redirectLoginCode = 401;
const redirectLoginMessage = "Access denied. Please log in first.";

const router = createBrowserRouter([
    {
        path: "/",
        element: <Navigate to="/start" />
    },
    {
        path: "*",
        element: <Navigate to="/start" />
    },
    {
        path: "/start",
        element: <StartPage />
    },
    {
        path: "/main",
        element: <App />
    },
    {
        path: "/getting-digit",
        element: <ImageProcesser />
    },
    {
        path: "/user",
        children: [
            {
                path: "register",
                element: <Register />
            },
            {
                path: "login",
                element: <Login />
            }
        ]
    }
]);

export default router;
export { redirectLoginCode, redirectLoginMessage };