import cv2
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image  # Pillow 모듈 사용
from datetime import datetime
import threading
# CustomTkinter 테마 설정 (라이트 모드 또는 다크 모드)
ctk.set_appearance_mode("light")  # "light" 또는 "dark"로 설정 가능

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Emergency Response System")
        self.geometry("800x600")
        
        # 창 크기 고정
        self.resizable(False, False)
        
        # 창 닫기 버튼(X)을 눌렀을 때의 동작 설정
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 배경 이미지 추가 (CTkImage 사용)
        try:
            bg_image = Image.open("background.jpg")  # 이미지 파일 경로를 정확히 지정하세요
            self.bg_image = ctk.CTkImage(light_image=bg_image, size=(800, 600))  # CTkImage로 변환하여 사용
            self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")  # CTkLabel에 이미지 적용
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)  # 배경 이미지를 창 전체에 맞춤
        except FileNotFoundError:
            print("배경 이미지를 찾을 수 없습니다. 경로를 확인하세요.")
        
        self.current_screen = None
        self.setup_ui()
        
    def setup_ui(self):
        # 각 화면을 초기화
        self.standby_screen = StandbyScreen(self)
        self.fire_screen = EmergencyScreen(self, "화재가 발생했습니다!", self.show_standby_screen)
        self.gas_screen = EmergencyScreen(self, "가스가 누출되었습니다!", self.show_standby_screen)
        self.report_screen = ReportScreen(self, self.show_standby_screen)
        self.doorlock_cam_screen = DoorlockCamScreen(self)
        
        # 대기 화면으로 시작
        self.show_standby_screen()

    def show_standby_screen(self):
        """대기 화면으로 전환"""
        if self.current_screen:
            self.current_screen.pack_forget()
        self.current_screen = self.standby_screen
        self.current_screen.pack(fill=ctk.BOTH, expand=True)

    def show_fire_screen(self):
        """화재 발생 화면으로 전환"""
        if self.current_screen:
            self.current_screen.pack_forget()
        self.current_screen = self.fire_screen
        self.current_screen.pack(fill=ctk.BOTH, expand=True)

    def show_gas_screen(self):
        """가스 누출 화면으로 전환"""
        if self.current_screen:
            self.current_screen.pack_forget()
        self.current_screen = self.gas_screen
        self.current_screen.pack(fill=ctk.BOTH, expand=True)

    def show_report_screen(self):
        """신고 접수 완료 화면으로 전환"""
        if self.current_screen:
            self.current_screen.pack_forget()
        self.current_screen = self.report_screen
        self.current_screen.pack(fill=ctk.BOTH, expand=True)

    def show_cancel_confirmation(self):
        """신고 취소 확인 화면을 현재 창에 표시"""
        if isinstance(self.current_screen, EmergencyScreen):
            # 현재 긴급 상황 화면의 모든 위젯 삭제 (완전히 제거)
            for widget in self.current_screen.winfo_children():
                widget.destroy()  # 완전히 삭제
            
            # 신고 취소 확인 메시지 및 버튼 표시
            ctk.CTkLabel(self.current_screen,
                         text="정말 신고를 취소하시겠습니까?",
                         font=("Helvetica", 24)).pack(pady=20)

            button_frame = ctk.CTkFrame(self.current_screen)
            button_frame.pack(pady=20)

            # 예 버튼 (취소 확정 시 대기화면으로 돌아감)
            ctk.CTkButton(button_frame,
                          text="예",
                          command=self.show_standby_screen,
                          width=200, height=100,
                          font=("Helvetica", 24)).pack(side=ctk.LEFT, padx=10)

            # 아니오 버튼 (취소하지 않고 다시 긴급 상황 화면으로 돌아감)
            ctk.CTkButton(button_frame,
                          text="아니오",
                          command=lambda: [self.restore_previous_emergency()],
                          width=200, height=100,
                          font=("Helvetica", 24)).pack(side=ctk.RIGHT, padx=10)

    def restore_previous_emergency(self):
        """긴급 상황 화면으로 복귀"""
        # 현재 신고 취소 확인 관련 UI 모두 삭제
        for widget in self.current_screen.winfo_children():
            widget.destroy()  # 신고 취소 확인 관련 UI 삭제

        # 긴급 상황 UI 다시 생성 (화재 발생 또는 가스 누출 상황 복구)
        if isinstance(self.current_screen, EmergencyScreen):
            message_label = ctk.CTkLabel(self.current_screen,
                                         text=self.current_screen.message_text,
                                         font=("Helvetica", 24))
            message_label.pack(pady=20)

            button_frame = ctk.CTkFrame(self.current_screen)
            button_frame.pack(pady=20)

            # 신고 확정 버튼 복구
            ctk.CTkButton(button_frame,
                          text="신고 확정",
                          command=self.show_report_screen,
                          width=200, height=100,
                          font=("Helvetica", 24)).pack(side=ctk.LEFT, padx=10)

            # 신고 취소 버튼 복구
            ctk.CTkButton(button_frame,
                          text="신고 취소",
                          command=self.show_cancel_confirmation,
                          width=200, height=100,
                          font=("Helvetica", 24)).pack(side=ctk.RIGHT, padx=10)
    
    def show_doorlock_cam_screen(self):
        """도어락 캠 스트리밍 화면으로 전환"""
        if self.current_screen:
            self.current_screen.pack_forget()
        self.current_screen = self.doorlock_cam_screen
        self.current_screen.pack(fill=ctk.BOTH, expand=True)
    
        # 도어락 캠 스트리밍 시작
        self.doorlock_cam_screen.start_streaming()

    def on_closing(self):
        """창 닫기 버튼(X)을 눌렀을 때 동작"""
        if messagebox.askokcancel("종료", "프로그램을 종료하시겠습니까?"):
            if hasattr(self, 'doorlock_cam_screen'):
                self.doorlock_cam_screen.on_closing()
            self.destroy()

class StandbyScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        # 중앙에 시계를 배치하기 위한 레이블 (크기 3배 확대 및 위치 상단으로 조정)
        self.clock_label = ctk.CTkLabel(self, text="", font=("Helvetica", 144))  # 글씨 크기를 3배로 키움 (48 -> 144)
        
        # 시계 위치를 위쪽으로 이동 (relx는 그대로 두고 rely를 줄여서 위로 이동)
        self.clock_label.place(relx=0.5, rely=0.3, anchor=ctk.CENTER)  # rely 값을 줄여서 시계를 위로 이동
        
        # 화재 발생 버튼 (크기 및 글씨 크기 조정)
        fire_button = ctk.CTkButton(self,
                                    text="화재 발생",
                                    command=lambda: master.show_fire_screen(),
                                    width=200, height=100,
                                    font=("Helvetica", 24))
        
        fire_button.place(relx=0.3, rely=0.8, anchor=ctk.CENTER)

        # 가스 누출 버튼 (크기 및 글씨 크기 조정)
        gas_button = ctk.CTkButton(self,
                                   text="가스 누출",
                                   command=lambda: master.show_gas_screen(),
                                   width=200, height=100,
                                   font=("Helvetica", 24))
        
        gas_button.place(relx=0.7, rely=0.8, anchor=ctk.CENTER)
        
        doorlock_button = ctk.CTkButton(self, text="도어락 캠", command=lambda: master.show_doorlock_cam_screen(),
                                width=200, height=100, font=("Helvetica", 24))
        doorlock_button.place(relx=0.5, rely=0.6, anchor=ctk.CENTER)
        # 시계 업데이트 시작
        self.update_clock()
        
    def update_clock(self):
        # 현재 시간을 HH:MM:SS 형식으로 표시
        current_time = datetime.now().strftime("%H:%M:%S")
        
        # 시계 레이블에 시간 설정
        self.clock_label.configure(text=current_time)
        
        # 1초마다 업데이트
        self.after(1000, self.update_clock)

class EmergencyScreen(ctk.CTkFrame):
    def __init__(self, master, message_text, cancel_callback):
       super().__init__(master)
       self.message_text = message_text  # 메시지 텍스트 저장

       # 메시지 표시 (화재 또는 가스 누출 상황)
       ctk.CTkLabel(self,
                    text=self.message_text,
                    font=("Helvetica", 24)).pack(pady=20)

       button_frame = ctk.CTkFrame(self)
       button_frame.pack(pady=20)

       # 신고 확정 버튼 (크기 및 글씨 크기 조정)
       ctk.CTkButton(button_frame,
                     text="신고 확정",
                     command=lambda: master.show_report_screen(),
                     width=200, height=100,
                     font=("Helvetica", 24)).pack(side=ctk.LEFT, padx=10)

       # 신고 취소 버튼 (크기 및 글씨 크기 조정 -> 현재 창에서 처리됨)
       ctk.CTkButton(button_frame,
                     text="신고 취소",
                     command=lambda: master.show_cancel_confirmation(),
                     width=200, height=100,
                     font=("Helvetica", 24)).pack(side=ctk.RIGHT, padx=10)

class ReportScreen(ctk.CTkFrame):
    def __init__(self, master, end_callback):
       super().__init__(master)
       
       # 신고 접수 완료 메시지 표시
       ctk.CTkLabel(self,
                    text="신고접수가 완료되었습니다!\n위험상황이 발생중입니다!",
                    font=("Helvetica", 24)).pack(pady=20)

       # 위험 상황 종료 버튼 추가 (크기 및 글씨 크기 조정)
       ctk.CTkButton(self,
                     text="위험상황 종료",
                     command=end_callback,
                     width=200, height=100,
                     font=("Helvetica", 24)).pack(pady=20)

class DoorlockCamScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        # 라벨: "도어락 벨소리 감지됨"
        self.alert_label = ctk.CTkLabel(self, text="도어락 벨소리 감지됨", font=("Helvetica", 24))
        self.alert_label.place(relx=0.5, rely=0.05, anchor=ctk.CENTER)
        
        # 스트리밍 화면 (크기를 더 크게 설정)
        self.video_label = ctk.CTkLabel(self, text="")
        self.video_label.place(relx=0.5, rely=0.4, anchor=ctk.CENTER)  # 위치를 중앙으로 설정
        
        # 확인완료 버튼 (화면 하단에 위치)
        self.confirm_button = ctk.CTkButton(self, text="확인완료", command=self.confirm_and_return,
                                            width=200, height=50, font=("Helvetica", 20))
        self.confirm_button.place(relx=0.5, rely=0.9, anchor=ctk.CENTER)
        
        # 웹캠 초기화
        self.cap = None
        self.stop_event = threading.Event()
    
    def start_streaming(self):
        """웹캠 스트리밍을 시작"""
        if not self.cap or not self.cap.isOpened():
            self.cap = cv2.VideoCapture(0)
            self.stop_event.clear()
            threading.Thread(target=self.update_frame, daemon=True).start()
    
    def update_frame(self):
        """웹캠에서 프레임을 읽어와 화면에 표시"""
        while not self.stop_event.is_set():
            ret, frame = self.cap.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)
                # 스트리밍 화면 크기를 더 크게 설정 (640x480)
                ctk_image = ctk.CTkImage(light_image=pil_image, size=(512, 384))
                self.video_label.configure(image=ctk_image)
                self.video_label.image = ctk_image  # 이미지 참조 유지
            cv2.waitKey(30)  # 약간의 지연을 추가하여 CPU 사용량 감소
    
    def confirm_and_return(self):
        """확인완료 버튼 클릭 시 대기화면으로 돌아감"""
        self.stop_event.set()
        if self.cap and self.cap.isOpened():
            self.cap.release()
        self.master.show_standby_screen()
    
    def on_closing(self):
        """창이 닫힐 때 웹캠 리소스 해제"""
        self.stop_event.set()
        if self.cap and self.cap.isOpened():
            self.cap.release()

if __name__ == "__main__":
    app = App()
    app.mainloop()