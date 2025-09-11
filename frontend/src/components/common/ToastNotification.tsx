import { useState, useEffect } from 'react';
import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from 'lucide-react';

export interface ToastProps {
    id: string;
    type: 'success' | 'error' | 'warning' | 'info';
    title: string;
    message: string;
    duration?: number;
    onClose: (id: string) => void;
    action?: {
        label: string;
        onClick: () => void;
    };
}

const ToastNotification: React.FC<ToastProps> = ({
    id,
    type,
    title,
    message,
    duration = 5000,
    onClose,
    action
}) => {
    const [isVisible, setIsVisible] = useState(false);
    const [isLeaving, setIsLeaving] = useState(false);

    useEffect(() => {
        // Animação de entrada
        const timer = setTimeout(() => setIsVisible(true), 10);
        return () => clearTimeout(timer);
    }, []);

    useEffect(() => {
        if (duration > 0) {
            const timer = setTimeout(() => {
                handleClose();
            }, duration);
            return () => clearTimeout(timer);
        }
    }, [duration]);

    const handleClose = () => {
        setIsLeaving(true);
        setTimeout(() => {
            onClose(id);
        }, 300);
    };

    const getIcon = () => {
        switch (type) {
            case 'success':
                return <CheckCircle className="w-5 h-5 text-green-600" />;
            case 'error':
                return <AlertCircle className="w-5 h-5 text-red-600" />;
            case 'warning':
                return <AlertTriangle className="w-5 h-5 text-yellow-600" />;
            case 'info':
                return <Info className="w-5 h-5 text-blue-600" />;
            default:
                return <Info className="w-5 h-5 text-gray-600" />;
        }
    };

    const getStyles = () => {
        const baseStyles = "relative flex items-start p-4 rounded-lg shadow-lg border-l-4 transition-all duration-300 ease-in-out transform";

        if (isLeaving) {
            return `${baseStyles} translate-x-full opacity-0`;
        }

        if (isVisible) {
            return `${baseStyles} translate-x-0 opacity-100`;
        }

        return `${baseStyles} translate-x-full opacity-0`;
    };

    const getTypeStyles = () => {
        switch (type) {
            case 'success':
                return 'bg-green-50 border-green-400 text-green-800';
            case 'error':
                return 'bg-red-50 border-red-400 text-red-800';
            case 'warning':
                return 'bg-yellow-50 border-yellow-400 text-yellow-800';
            case 'info':
                return 'bg-blue-50 border-blue-400 text-blue-800';
            default:
                return 'bg-gray-50 border-gray-400 text-gray-800';
        }
    };

    return (
        <div className={`${getStyles()} ${getTypeStyles()} min-w-80 max-w-md`}>
            <div className="flex-shrink-0 mr-3">
                {getIcon()}
            </div>

            <div className="flex-1 min-w-0">
                <h4 className="text-sm font-semibold mb-1">
                    {title}
                </h4>
                <p className="text-sm opacity-90">
                    {message}
                </p>

                {action && (
                    <div className="mt-3">
                        <button
                            onClick={action.onClick}
                            className="text-sm font-medium underline hover:no-underline focus:outline-none focus:underline"
                        >
                            {action.label}
                        </button>
                    </div>
                )}
            </div>

            <button
                onClick={handleClose}
                className="flex-shrink-0 ml-3 text-gray-400 hover:text-gray-600 focus:outline-none focus:text-gray-600 transition-colors duration-200"
            >
                <X className="w-4 h-4" />
            </button>
        </div>
    );
};

export default ToastNotification;
