// src/interfaces.ts

export interface Trade {
    id: number;
    timestamp: string;
    asset: string;
    buy_exchange: string;
    sell_exchange: string;
    buy_price: number;
    sell_price: number;
    amount: number;
    gross_profit: number;
    buy_fee: number;
    sell_fee: number;
    withdrawal_fee: number;
    buy_slippage: number;
    sell_slippage: number;
    latency: number;
    estimated_price_change: number;
    profit: number;
    profit_percentage: number;
    net_profit?: number; // Optional alias
}

export interface ArbitrageOpportunity {
    timestamp: string;
    exchange_buy: string;
    exchange_sell: string;
    currency: string;
    buy_price: number;
    sell_price: number;
    gross_profit: number;
    net_profit: number;          // Added property
    profit_percentage: number;
    buy_fee: number;
    sell_fee: number;
    withdrawal_fee: number;
    buy_slippage: number;
    sell_slippage: number;
    latency: number;
    estimated_price_change: number;
}

export interface BacktestResult {
    total_profit: number;
    trades: Trade[];
}

// src/interfaces.tsx

export interface ProfitLossSummary {
    total_gross_profit: number;
    total_net_profit: number;
    // total_loss removed
}


export interface MarketData {
    symbol: string;
    exchange: string;
    price: number;
}
