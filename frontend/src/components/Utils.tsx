import { FaCheckCircle, FaWallet } from "react-icons/fa"
import { HiMiniBanknotes } from "react-icons/hi2"



export const BalanceIcon = ({ balance }: { balance: number }) => {
    return balance == 0?<FaCheckCircle color="lime" size={23} />:(balance<0?<FaWallet color="red" size={23} />:<HiMiniBanknotes color="orange" size={24} />)
}