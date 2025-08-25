import React from 'react';

interface StatusBadgeProps {
    status: string;
    className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, className = '' }) => {
    const getStatusConfig = (status: string) => {
        const statusConfigs = {
            'RASCUNHO': {
                bgColor: 'bg-gray-100',
                textColor: 'text-gray-800',
                borderColor: 'border-gray-300',
                icon: '📝'
            },
            'PENDENTE': {
                bgColor: 'bg-yellow-100',
                textColor: 'text-yellow-800',
                borderColor: 'border-yellow-300',
                icon: '⏳'
            },
            'ENVIADA': {
                bgColor: 'bg-blue-100',
                textColor: 'text-blue-800',
                borderColor: 'border-blue-300',
                icon: '📤'
            },
            'APROVADA': {
                bgColor: 'bg-green-100',
                textColor: 'text-green-800',
                borderColor: 'border-green-300',
                icon: '✅'
            },
            'REJEITADA': {
                bgColor: 'bg-red-100',
                textColor: 'text-red-800',
                borderColor: 'border-red-300',
                icon: '❌'
            },
            'REALIZADA': {
                bgColor: 'bg-purple-100',
                textColor: 'text-purple-800',
                borderColor: 'border-purple-300',
                icon: '🎯'
            },
            'CANCELADA': {
                bgColor: 'bg-gray-100',
                textColor: 'text-gray-600',
                borderColor: 'border-gray-300',
                icon: '🚫'
            }
        };

        return statusConfigs[status as keyof typeof statusConfigs] || {
            bgColor: 'bg-gray-100',
            textColor: 'text-gray-800',
            borderColor: 'border-gray-300',
            icon: '❓'
        };
    };

    const config = getStatusConfig(status);

    return (
        <span
            className={`
        inline-flex items-center px-3 py-1 rounded-full text-xs font-medium
        border ${config.bgColor} ${config.textColor} ${config.borderColor}
        transition-all duration-200 hover:shadow-sm
        ${className}
      `}
        >
            <span className="mr-1">{config.icon}</span>
            {status}
        </span>
    );
};
