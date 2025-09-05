// 🎨 Design System Unificado - Passos da Proposta
// Sistema de tokens de design para garantir consistência visual

export const DESIGN_TOKENS = {
    // 🎯 CORES PRINCIPAIS
    colors: {
        // Cor da marca - APENAS para botões e elementos de ação
        primary: {
            DEFAULT: '#2563eb', // custom-blue
            light: '#dbeafe',   // custom-blue-light
            dark: '#1e40af',   // custom-blue-dark
            hover: '#1d4ed8',  // custom-blue-light (hover)
        },

        // Cores neutras para elementos não-interativos
        neutral: {
            white: '#ffffff',
            gray: {
                50: '#f9fafb',
                100: '#f3f4f6',
                200: '#e5e7eb',
                300: '#d1d5db',
                400: '#9ca3af',
                500: '#6b7280',
                600: '#4b5563',
                700: '#374151',
                800: '#1f2937',
                900: '#111827',
            }
        },

        // Cores semânticas
        semantic: {
            success: {
                DEFAULT: '#10b981',
                light: '#d1fae5',
                dark: '#059669',
            },
            warning: {
                DEFAULT: '#f59e0b',
                light: '#fef3c7',
                dark: '#d97706',
            },
            error: {
                DEFAULT: '#ef4444',
                light: '#fee2e2',
                dark: '#dc2626',
            },
            info: {
                DEFAULT: '#3b82f6',
                light: '#dbeafe',
                dark: '#2563eb',
            }
        }
    },

    // 📏 ESPAÇAMENTOS
    spacing: {
        xs: '0.25rem',   // 4px
        sm: '0.5rem',    // 8px
        md: '1rem',      // 16px
        lg: '1.5rem',    // 24px
        xl: '2rem',      // 32px
        '2xl': '3rem',   // 48px
        '3xl': '4rem',   // 64px
    },

    // 🔤 TIPOGRAFIA
    typography: {
        sizes: {
            xs: '0.75rem',    // 12px
            sm: '0.875rem',   // 14px
            base: '1rem',     // 16px
            lg: '1.125rem',   // 18px
            xl: '1.25rem',    // 20px
            '2xl': '1.5rem',  // 24px
            '3xl': '1.875rem', // 30px
        },
        weights: {
            normal: '400',
            medium: '500',
            semibold: '600',
            bold: '700',
        }
    },

    // 🎭 SOMBRAS
    shadows: {
        sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
        DEFAULT: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
        md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
        lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
    },

    // 🔄 TRANSIÇÕES
    transitions: {
        fast: '150ms ease-in-out',
        DEFAULT: '200ms ease-in-out',
        slow: '300ms ease-in-out',
    },

    // 📐 BORDAS
    borders: {
        radius: {
            sm: '0.25rem',   // 4px
            DEFAULT: '0.5rem', // 8px
            md: '0.75rem',   // 12px
            lg: '1rem',      // 16px
            xl: '1.5rem',    // 24px
            full: '9999px',
        },
        width: {
            DEFAULT: '1px',
            thick: '2px',
        }
    }
} as const;

// 🎨 FUNÇÕES AUXILIARES PARA CLASSES CSS
export const getColorClasses = {
    // Botões primários (custom-blue)
    primaryButton: 'bg-custom-blue text-white hover:bg-custom-blue-light focus:ring-2 focus:ring-custom-blue focus:ring-offset-2',
    primaryButtonDisabled: 'bg-gray-300 text-gray-500 cursor-not-allowed',

    // Botões secundários
    secondaryButton: 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50 focus:ring-2 focus:ring-custom-blue focus:ring-offset-2',

    // Cards e containers
    card: 'bg-white border border-gray-200 rounded-lg shadow-sm',
    cardSelected: 'bg-white border-custom-blue border-2 shadow-md',
    cardHover: 'hover:border-gray-300 hover:shadow-md transition-shadow',

    // Textos
    textPrimary: 'text-gray-900',
    textSecondary: 'text-gray-600',
    textMuted: 'text-gray-500',
    textSuccess: 'text-green-600',
    textWarning: 'text-yellow-600',
    textError: 'text-red-600',

    // Fundos
    background: 'bg-gray-50',
    backgroundLight: 'bg-white',
    backgroundInfo: 'bg-blue-50 border border-blue-200',
    backgroundSuccess: 'bg-green-50 border border-green-200',
    backgroundWarning: 'bg-yellow-50 border border-yellow-200',
    backgroundError: 'bg-red-50 border border-red-200',

    // Inputs
    input: 'border border-gray-300 rounded-lg focus:ring-2 focus:ring-custom-blue focus:border-transparent',
    inputError: 'border-red-300 focus:ring-red-500',

    // Abas
    tabActive: 'border-custom-blue text-custom-blue',
    tabInactive: 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
    tabDisabled: 'border-transparent text-gray-300 cursor-not-allowed',
} as const;

// 🎯 FUNÇÃO PARA GERAR CLASSES DE CORES DINÂMICAS
export const generateColorClasses = (variant: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info') => {
    const variants = {
        primary: {
            bg: 'bg-custom-blue',
            text: 'text-white',
            border: 'border-custom-blue',
            hover: 'hover:bg-custom-blue-light',
            focus: 'focus:ring-custom-blue',
        },
        secondary: {
            bg: 'bg-white',
            text: 'text-gray-700',
            border: 'border-gray-300',
            hover: 'hover:bg-gray-50',
            focus: 'focus:ring-gray-500',
        },
        success: {
            bg: 'bg-green-600',
            text: 'text-white',
            border: 'border-green-600',
            hover: 'hover:bg-green-700',
            focus: 'focus:ring-green-500',
        },
        warning: {
            bg: 'bg-yellow-600',
            text: 'text-white',
            border: 'border-yellow-600',
            hover: 'hover:bg-yellow-700',
            focus: 'focus:ring-yellow-500',
        },
        error: {
            bg: 'bg-red-600',
            text: 'text-white',
            border: 'border-red-600',
            hover: 'hover:bg-red-700',
            focus: 'focus:ring-red-500',
        },
        info: {
            bg: 'bg-blue-600',
            text: 'text-white',
            border: 'border-blue-600',
            hover: 'hover:bg-blue-700',
            focus: 'focus:ring-blue-500',
        },
    };

    return variants[variant];
};

// 🎨 FUNÇÃO PARA GERAR CLASSES DE ESPAÇAMENTO
export const getSpacingClasses = (size: keyof typeof DESIGN_TOKENS.spacing) => {
    return DESIGN_TOKENS.spacing[size];
};

// 🎯 FUNÇÃO PARA GERAR CLASSES DE TIPOGRAFIA
export const getTypographyClasses = (size: keyof typeof DESIGN_TOKENS.typography.sizes, weight?: keyof typeof DESIGN_TOKENS.typography.weights) => {
    const sizeClass = `text-${size}`;
    const weightClass = weight ? `font-${weight}` : '';
    return `${sizeClass} ${weightClass}`.trim();
};

// 🎭 FUNÇÃO PARA GERAR CLASSES DE SOMBRA
export const getShadowClasses = (shadow: keyof typeof DESIGN_TOKENS.shadows) => {
    return `shadow-${shadow}`;
};

// 🔄 FUNÇÃO PARA GERAR CLASSES DE TRANSIÇÃO
export const getTransitionClasses = (transition: keyof typeof DESIGN_TOKENS.transitions) => {
    return `transition-all duration-${transition}`;
};

// 📐 FUNÇÃO PARA GERAR CLASSES DE BORDA
export const getBorderClasses = (radius: keyof typeof DESIGN_TOKENS.borders.radius, width?: keyof typeof DESIGN_TOKENS.borders.width) => {
    const radiusClass = `rounded-${radius}`;
    const widthClass = width ? `border-${width}` : 'border';
    return `${widthClass} ${radiusClass}`.trim();
};

// 🎯 VALIDAÇÃO DE CORES PARA ACESSIBILIDADE
export const validateColorContrast = (foreground: string, background: string): boolean => {
    // Implementação simplificada - em produção usar biblioteca específica
    const contrastRatios = {
        'white-black': 21,
        'white-gray-900': 18.5,
        'white-gray-800': 15.3,
        'white-gray-700': 12.6,
        'white-gray-600': 9.5,
        'white-gray-500': 6.7,
        'white-gray-400': 4.5,
        'white-gray-300': 3.0,
        'white-gray-200': 2.0,
        'white-gray-100': 1.4,
        'white-gray-50': 1.1,
    };

    const key = `${foreground}-${background}`;
    return contrastRatios[key as keyof typeof contrastRatios] >= 4.5; // WCAG AA
};

// 🎨 EXPORTAÇÃO DE TODAS AS FUNÇÕES AUXILIARES
export const designUtils = {
    colors: getColorClasses,
    generateColorClasses,
    spacing: getSpacingClasses,
    typography: getTypographyClasses,
    shadows: getShadowClasses,
    transitions: getTransitionClasses,
    borders: getBorderClasses,
    validateContrast: validateColorContrast,
} as const;

export default DESIGN_TOKENS;
