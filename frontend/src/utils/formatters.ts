export const formatInteger = (value: number) => new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 }).format(value)
export const formatPercent = (value: number) => `${value.toFixed(1)}%`
export const formatCurrency = (value: number) => new Intl.NumberFormat('en-GB', { style: 'currency', currency: 'GBP', minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(value)
export const formatDecimal = (value: number, digits = 3) => value.toFixed(digits)
export const formatDate = (value: string) => new Intl.DateTimeFormat('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }).format(new Date(value))
